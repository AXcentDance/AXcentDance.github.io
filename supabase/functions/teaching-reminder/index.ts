// Teaching reminder: emails a teacher when a class they are assigned to
// happened more than 24h ago and its presences were never logged.
//
// Class occurrences are derived from the recurring slot ("Tue 19:30 ...")
// rather than stored, so nothing has to be pre-created. A session counts as
// logged when any attendance row exists for (class_value, class_date).
// Every reminder actually sent is recorded in teaching_reminders, so a
// teacher is never emailed twice about the same session.
//
// Invoked daily by pg_cron (see migration 20260720250000) late enough that
// the previous evening's classes are safely past the 24h mark.
// Deploy: supabase functions deploy teaching-reminder --no-verify-jwt
// Secrets: CRON_SECRET, RESEND_API_KEY (+ SUPABASE_* set automatically)

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const DAY_NUMBERS: Record<string, number> = {
  Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6,
}
const LOOKBACK_DAYS = 14   // ignore anything older, so enabling this is not a flood
const GRACE_HOURS = 24

serve(async (req) => {
  if (req.headers.get('x-cron-secret') !== Deno.env.get('CRON_SECRET')) {
    return new Response('Forbidden', { status: 403 })
  }

  const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')
  const supabaseAdmin = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
  )

  const [assignRes, attRes, sentRes, sessRes, teacherRes] = await Promise.all([
    supabaseAdmin.from('class_teachers')
      .select('class_value, teachers ( id, email, first_name, active )'),
    supabaseAdmin.from('attendance').select('class_value, class_date'),
    supabaseAdmin.from('teaching_reminders').select('class_value, class_date, teacher_id'),
    supabaseAdmin.from('class_sessions').select('class_value, class_date, teacher_id'),
    supabaseAdmin.from('teachers').select('id, email, first_name, active'),
  ])

  const err = assignRes.error || attRes.error || sentRes.error || sessRes.error || teacherRes.error
  if (err) {
    console.error('Query failed:', err)
    return new Response(JSON.stringify({ ok: false, error: err.message }), { status: 500 })
  }

  const logged = new Set((attRes.data ?? []).map(a => `${a.class_value}|${a.class_date}`))
  const alreadySent = new Set((sentRes.data ?? [])
    .map(r => `${r.class_value}|${r.class_date}|${r.teacher_id}`))

  // A single-date override (someone covered while the usual teacher was
  // away) decides who is actually chased for that session.
  type TeacherRow = { id: string; email: string; first_name: string | null; active: boolean }
  const teacherById = new Map<string, TeacherRow>(
    (teacherRes.data ?? []).map((t: TeacherRow) => [t.id, t]))
  const overrideFor = new Map<string, string | null>(
    (sessRes.data ?? []).map(s => [`${s.class_value}|${s.class_date}`, s.teacher_id]))

  // "Now" in studio time; a class is due once GRACE_HOURS have passed since
  // its start time on its own date.
  const zurichNow = new Date(new Date().toLocaleString('en-US', { timeZone: 'Europe/Zurich' }))
  const iso = (d: Date) => d.getFullYear() + '-' +
    String(d.getMonth() + 1).padStart(2, '0') + '-' +
    String(d.getDate()).padStart(2, '0')

  let sent = 0
  const skipped: string[] = []
  const failures: string[] = []

  for (const row of assignRes.data ?? []) {
    const assigned = (row as { teachers: TeacherRow | null }).teachers
    if (!assigned) continue

    const slot = String(row.class_value).match(/^(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (\d{1,2}):(\d{2}) (.*)$/)
    if (!slot) continue
    const [, dayAbbr, hh, mm, className] = slot
    const weekday = DAY_NUMBERS[dayAbbr]

    for (let back = 1; back <= LOOKBACK_DAYS; back++) {
      const d = new Date(zurichNow)
      d.setDate(d.getDate() - back)
      if (d.getDay() !== weekday) continue

      const dateStr = iso(d)
      const key = `${row.class_value}|${dateStr}`
      if (logged.has(key)) continue                                  // presences are in

      // Chase whoever actually taught: the substitute if one was recorded,
      // otherwise the regular teacher. An override to "nobody" (teacher_id
      // cleared) means the class did not run, so nobody is chased.
      let teacher = assigned
      if (overrideFor.has(key)) {
        const subId = overrideFor.get(key)
        if (!subId) continue
        const sub = teacherById.get(subId)
        if (!sub) continue
        teacher = sub
      }
      if (!teacher.active) continue
      if (alreadySent.has(`${key}|${teacher.id}`)) continue          // already nudged

      const classStart = new Date(d)
      classStart.setHours(Number(hh), Number(mm), 0, 0)
      if ((zurichNow.getTime() - classStart.getTime()) < GRACE_HOURS * 3600 * 1000) continue

      const prettyDate = new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
        weekday: 'long', month: 'long', day: 'numeric',
      })

      if (!RESEND_API_KEY) {
        console.warn('RESEND_API_KEY not set; skipping', key)
        skipped.push(key)
        continue
      }

      try {
        const res = await fetch('https://api.resend.com/emails', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${RESEND_API_KEY}`,
          },
          body: JSON.stringify({
            from: 'AXcent Dance <info@axcentdance.com>',
            to: [teacher.email],
            subject: `Attendance still missing — ${className}, ${prettyDate}`,
            html: `
              <div style="font-family: sans-serif; color: #333; line-height: 1.6;">
                <h1>Quick reminder, ${teacher.first_name || 'there'}</h1>
                <p>The presences for <strong>${className}</strong> on
                  <strong>${prettyDate} at ${hh}:${mm}</strong> have not been logged yet.</p>
                <p>Could you add them when you get a moment? It keeps everyone's pass
                  and 10-class balance accurate.</p>
                <div style="margin: 24px 0;">
                  <a href="https://axcentdance.com/_attendance"
                     style="background: #E8B04B; color: #10231F; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                    Log the presences
                  </a>
                </div>
                <p>Thank you!</p>
                <p><em>AXcent Dance Zurich</em></p>
              </div>
            `,
          }),
        })
        if (!res.ok) throw new Error(`Resend responded ${res.status}: ${await res.text()}`)

        const { error: markError } = await supabaseAdmin.from('teaching_reminders').insert({
          class_value: row.class_value, class_date: dateStr, teacher_id: teacher.id,
        })
        if (markError) console.error(`Sent to ${teacher.email} but could not record:`, markError)

        sent++
        console.log(`Teaching reminder sent to ${teacher.email} for ${key}`)
      } catch (e) {
        failures.push(`${teacher.email} ${key}`)
        console.error(`Reminder failed for ${key}:`, e)
      }
    }
  }

  return new Response(JSON.stringify({ ok: true, sent, skipped, failures }), {
    headers: { 'Content-Type': 'application/json' },
  })
})
