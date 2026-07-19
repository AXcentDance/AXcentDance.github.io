// Stripe webhook: activates the buyer's pending registration after checkout.
// Deploy: supabase functions deploy stripe-webhook
// Secrets required: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, RESEND_API_KEY,
//                   SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (set automatically)

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import Stripe from 'https://esm.sh/stripe@11.1.0?target=deno'

serve(async (req) => {
  const signature = req.headers.get('Stripe-Signature')
  if (!signature) {
    return new Response("No signature", { status: 400 })
  }

  const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY') ?? '', {
    apiVersion: '2022-11-15',
    httpClient: Stripe.createFetchHttpClient(),
  })

  const body = await req.text()
  let event

  try {
    event = await stripe.webhooks.constructEventAsync(
      body,
      signature,
      Deno.env.get('STRIPE_WEBHOOK_SECRET') ?? ''
    )
  } catch (err) {
    console.error(`Webhook signature verification failed: ${err.message}`)
    return new Response(err.message, { status: 400 })
  }

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object
    // registration.html appends both prefilled_email and client_reference_id
    // to the Payment Link, so client_reference_id is the reliable fallback if
    // the buyer changes the email on Stripe's checkout page.
    const customerEmail = session.customer_details?.email || session.client_reference_id

    if (customerEmail) {
      const supabaseAdmin = createClient(
        Deno.env.get('SUPABASE_URL') ?? '',
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
      )

      // Paid portal requests (private class / bootcamp) are recognised by
      // their amount, which does not overlap with any class-pass price.
      const paidRequestType = requestTypeForAmount(session.amount_total)
      if (paidRequestType) {
        await confirmPaidRequest(supabaseAdmin, paidRequestType, customerEmail, session)
        return new Response("Received", { status: 200 })
      }

      // Activate the newest pending registration for this email. The status
      // filter makes replayed webhook events a no-op.
      const { data: pending, error: findError } = await supabaseAdmin
        .from('registrations')
        .select('id')
        .ilike('email', customerEmail)
        .eq('status', 'pending_payment')
        .order('created_at', { ascending: false })
        .limit(1)

      if (findError) {
        console.error('Error finding registration:', findError)
      } else if (!pending || pending.length === 0) {
        console.warn(`No pending registration found for ${customerEmail}`)
      } else {
        const { error: updateError } = await supabaseAdmin
          .from('registrations')
          .update({ status: 'active', stripe_session_id: session.id })
          .eq('id', pending[0].id)

        if (updateError) {
          console.error('Error activating registration:', updateError)
        } else {
          console.log(`Registration ${pending[0].id} activated for ${customerEmail}`)
          await sendWelcomeEmail(customerEmail, session.customer_details?.name || 'Dancer')
        }
      }
    }
  }

  return new Response("Received", { status: 200 })
})

// Amounts are in cents. Private packages: 150 / 360 / 550 CHF; bootcamp
// full pass: 115 CHF. None of these collide with a class-pass price
// (185-450 CHF regular/student tiers, 255/300 CHF flexible).
const PRIVATE_AMOUNTS: Record<number, string> = {
  15000: '1 hour — 150 CHF',
  36000: '3 hours — 360 CHF',
  55000: '5 hours — 550 CHF',
}
const BOOTCAMP_AMOUNT = 11500

function requestTypeForAmount(amountTotal: number | null): 'private_class' | 'bootcamp' | null {
  if (!amountTotal) return null
  if (PRIVATE_AMOUNTS[amountTotal]) return 'private_class'
  if (amountTotal === BOOTCAMP_AMOUNT) return 'bootcamp'
  return null
}

const OWNER_NOTIFY_EMAIL = 'info@axcentdance.com'
const REQUESTS_SHEET_URL = 'https://script.google.com/macros/s/AKfycbxJXXjTchZywrtg9cqW2wkmd85t7xt2LD5hc8jZNibZ0n7s0YCRU64g9w7RhkzqXk94/exec'

// Flip the newest matching pending_payment request to 'new' so it appears
// in the owner inbox, then notify the owner and mirror to the Sheet.
// The status filter makes replayed webhook events a no-op.
async function confirmPaidRequest(
  supabaseAdmin: ReturnType<typeof createClient>,
  type: 'private_class' | 'bootcamp',
  email: string,
  session: { amount_total: number | null; customer_details?: { name?: string | null } | null },
) {
  const { data: rows, error: findError } = await supabaseAdmin
    .from('requests')
    .select('*')
    .ilike('email', email)
    .eq('type', type)
    .eq('status', 'pending_payment')
    .order('created_at', { ascending: false })
    .limit(1)

  if (findError) {
    console.error('Error finding pending request:', findError)
    return
  }
  if (!rows || rows.length === 0) {
    // e.g. a bootcamp ticket bought on the public page — no portal row exists.
    console.warn(`No pending ${type} request found for ${email}`)
    return
  }

  const request = rows[0]
  const { error: updateError } = await supabaseAdmin
    .from('requests')
    .update({ status: 'new' })
    .eq('id', request.id)

  if (updateError) {
    console.error('Error confirming paid request:', updateError)
    return
  }
  console.log(`Paid ${type} request ${request.id} confirmed for ${email}`)

  const typeLabel = type === 'private_class' ? 'Private Class (PAID)' : 'Dominican Bootcamp (PAID)'
  const amountLabel = session.amount_total ? `${(session.amount_total / 100).toFixed(2)} CHF` : 'unknown'

  // Owner notification via FormSubmit (already activated for this address).
  try {
    await fetch(`https://formsubmit.co/ajax/${OWNER_NOTIFY_EMAIL}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({
        _subject: `Paid ${type === 'private_class' ? 'Private Class' : 'Bootcamp'} Request: ${email}`,
        _template: 'table',
        _captcha: 'false',
        Email: email,
        Name: request.name || session.customer_details?.name || 'Unknown',
        Type: typeLabel,
        Paid: amountLabel,
        From: request.date_from || 'N/A',
        Until: request.date_until || 'N/A',
        Details: request.details || 'None',
      }),
    })
  } catch (err) {
    console.error('Owner notification email failed:', err)
  }

  // Sheet mirror (append-only submission log).
  try {
    await fetch(REQUESTS_SHEET_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: `${type} (paid ${amountLabel})`,
        name: request.name || '',
        email: email,
        date_from: request.date_from || '',
        date_until: request.date_until || '',
        details: request.details || '',
      }),
      redirect: 'follow',
    })
  } catch (err) {
    console.error('Sheet mirror failed:', err)
  }
}

async function sendWelcomeEmail(email: string, name: string) {
  const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')
  if (!RESEND_API_KEY) {
    console.warn('RESEND_API_KEY not set; skipping welcome email')
    return
  }

  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${RESEND_API_KEY}`
      },
      body: JSON.stringify({
        from: 'AXcent Dance <info@axcentdance.com>',
        to: [email],
        subject: 'Welcome to the AXcent Family! 💃',
        html: `
          <div style="font-family: sans-serif; color: #333; line-height: 1.6;">
            <h1>Welcome, ${name}!</h1>
            <p>We are thrilled to have you join us at <strong>AXcent Dance</strong>.</p>
            <p>Your registration and payment have been received successfully. You are all set to start your dance journey with us!</p>

            <div style="background: #f4f4f4; padding: 15px; border-radius: 8px; margin: 20px 0;">
              <strong>Next Steps:</strong>
              <ul>
                <li>Check the <a href="https://axcentdance.com/schedule">Schedule</a> for your class times.</li>
                <li>Create your account on the <a href="https://axcentdance.com/portal.html">Student Portal</a> to see your pass and declare absence days.</li>
              </ul>
            </div>

            <p>If you have any questions, just reply to this email.</p>
            <p>See you on the dance floor!</p>
            <p><em>Ale & Xidan</em><br>AXcent Dance Zurich</p>
          </div>
        `
      })
    });

    const data = await res.json();
    console.log('Email sent:', data);
  } catch (err) {
    console.error('Error sending email:', err);
  }
}
