// Renewal reminder: emails every student whose active pass ends inside the
// current Mon-Sun week (Europe/Zurich) and has not been reminded yet.
// Invoked daily by pg_cron (see migration 20260720120000) so the reminder
// lands on Monday morning and self-heals if a run fails. Idempotent via
// registrations.renewal_reminder_sent_at, which resets when a pass is
// extended.
// Deploy: supabase functions deploy renewal-reminder --no-verify-jwt
// Secrets: CRON_SECRET, RESEND_API_KEY (+ SUPABASE_* set automatically)

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  if (req.headers.get('x-cron-secret') !== Deno.env.get('CRON_SECRET')) {
    return new Response('Forbidden', { status: 403 })
  }

  const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')
  if (!RESEND_API_KEY) {
    console.error('RESEND_API_KEY not set; cannot send reminders')
    return new Response(JSON.stringify({ ok: false, error: 'RESEND_API_KEY not set' }), { status: 500 })
  }

  const supabaseAdmin = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
  )

  // Current Mon-Sun week in studio time.
  const zurichNow = new Date(new Date().toLocaleString('en-US', { timeZone: 'Europe/Zurich' }))
  zurichNow.setHours(0, 0, 0, 0)
  const monday = new Date(zurichNow)
  monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7))
  const sunday = new Date(monday)
  sunday.setDate(sunday.getDate() + 6)
  const iso = (d: Date) => d.getFullYear() + '-' +
    String(d.getMonth() + 1).padStart(2, '0') + '-' +
    String(d.getDate()).padStart(2, '0')

  const { data: ending, error } = await supabaseAdmin
    .from('registrations')
    .select('id, email, first_name, pass_type, pass_end_date, selected_classes')
    .eq('status', 'active')
    .gte('pass_end_date', iso(monday))
    .lte('pass_end_date', iso(sunday))
    .is('renewal_reminder_sent_at', null)

  if (error) {
    console.error('Query failed:', error)
    return new Response(JSON.stringify({ ok: false, error: error.message }), { status: 500 })
  }

  // A pass can end mid-week (sick-day and freeze extensions land on class
  // days), so spell out which enrolled classes are still covered in the
  // final week and which fall after the end date.
  const DAY_NUM: Record<string, number> = { Mon: 0, Tue: 1, Wed: 2, Thu: 3, Fri: 4, Sat: 5, Sun: 6 }
  function finalWeekClasses(selectedClasses: string | null, endIso: string) {
    const covered: string[] = []
    const missed: string[] = []
    for (const raw of (selectedClasses || '').split(', ')) {
      const entry = raw.trim().replace(/ \((Leader|Follower)\)$/, '')
      const m = entry.match(/^(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (\d{1,2}:\d{2}) (.*)$/)
      if (!m) continue
      const d = new Date(monday)
      d.setDate(d.getDate() + DAY_NUM[m[1]])
      const label = d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) +
        ' — ' + m[3] + ' at ' + m[2]
      if (iso(d) <= endIso) covered.push(label)
      else missed.push(label)
    }
    return { covered, missed }
  }

  let sent = 0
  const failures: string[] = []

  for (const reg of ending ?? []) {
    const endDate = new Date(reg.pass_end_date + 'T00:00:00').toLocaleDateString('en-US', {
      weekday: 'long', month: 'long', day: 'numeric'
    })
    const { covered, missed } = finalWeekClasses(reg.selected_classes, reg.pass_end_date)
    const classesHtml =
      (covered.length
        ? `<p><strong>Still included before your pass ends:</strong></p>
           <ul>${covered.map(c => `<li>${c}</li>`).join('')}</ul>`
        : '') +
      (missed.length
        ? `<p><strong>Please note:</strong> ${missed.join('; ')} — ${missed.length === 1 ? 'this class falls' : 'these classes fall'}
           after your pass ends and ${missed.length === 1 ? 'is' : 'are'} not covered anymore.
           Renew now and you will not miss ${missed.length === 1 ? 'it' : 'them'}.</p>`
        : '')
    try {
      const res = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${RESEND_API_KEY}`
        },
        body: JSON.stringify({
          from: 'AXcent Dance <info@axcentdance.com>',
          to: [reg.email],
          subject: 'Your last week of classes — keep your spot',
          html: `
            <div style="font-family: sans-serif; color: #333; line-height: 1.6;">
              <h1>One more week, ${reg.first_name || 'dancer'}!</h1>
              <p>This is the final week of your current pass — it ends on <strong>${endDate}</strong>.</p>
              ${classesHtml}
              <p>To keep your spot in class without missing a week, you can renew in under a minute
                from your <a href="https://axcentdance.com/portal.html">Student Portal</a>:
                your package, classes, and details are already prefilled.</p>
              <div style="margin: 24px 0;">
                <a href="https://axcentdance.com/portal.html"
                   style="background: #E8B04B; color: #10231F; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                  Renew Your Pass
                </a>
              </div>
              <p>Thinking about a different class or level for the next block? Just reply to this
                email — we are happy to find the right fit together.</p>
              <p>See you on the dance floor!</p>
              <p><em>Ale &amp; Xidan</em><br>AXcent Dance Zurich</p>
            </div>
          `
        })
      })
      if (!res.ok) throw new Error(`Resend responded ${res.status}: ${await res.text()}`)

      const { error: markError } = await supabaseAdmin
        .from('registrations')
        .update({ renewal_reminder_sent_at: new Date().toISOString() })
        .eq('id', reg.id)
      if (markError) {
        // Email went out but the flag failed — log loudly, a duplicate may
        // follow tomorrow, which is preferable to silence.
        console.error(`Sent to ${reg.email} but could not mark:`, markError)
      }
      sent++
      console.log(`Renewal reminder sent to ${reg.email} (pass ends ${reg.pass_end_date})`)
    } catch (err) {
      failures.push(reg.email)
      console.error(`Reminder to ${reg.email} failed:`, err)
    }
  }

  return new Response(JSON.stringify({ ok: true, week: iso(monday) + '..' + iso(sunday), sent, failures }), {
    headers: { 'Content-Type': 'application/json' }
  })
})
