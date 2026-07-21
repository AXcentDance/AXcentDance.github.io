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
    // The buyer's email as entered on Stripe's checkout page. If they paid
    // with a different address than their registration, the pending row is
    // not found and the payment surfaces in the logs / Stripe dashboard for
    // manual matching. (client_reference_id is not used: Stripe silently
    // drops non-alphanumeric values such as emails on Payment Links.)
    const customerEmail = session.customer_details?.email

    if (customerEmail) {
      const supabaseAdmin = createClient(
        Deno.env.get('SUPABASE_URL') ?? '',
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
      )

      // Paid portal requests (private class / bootcamp) are recognised by
      // the Payment Link that created the session — stable across price
      // changes, renames, and promotion codes.
      const paidRequest = session.payment_link ? REQUEST_LINKS[session.payment_link] : null
      if (paidRequest) {
        await confirmPaidRequest(supabaseAdmin, paidRequest.type, customerEmail, session)
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

// Payment Links for paid portal requests, keyed by plink id (present in
// every checkout.session.completed event as session.payment_link). Link ids
// survive price changes, product renames, and promotion codes; any session
// from an unlisted link falls through to the class-pass registration path.
//   private 1h  https://buy.stripe.com/cNi00l7QX6XT5O760qfnO0g
//   private 3h  https://buy.stripe.com/00w4gB9Z54PLa4nfB0fnO0h
//   private 5h  https://buy.stripe.com/4gMcN77QX4PLdgz2OefnO0i
//   bootcamp    https://buy.stripe.com/8x214p2wDgyt2BV9cCfnO0a
const REQUEST_LINKS: Record<string, { type: 'private_class' | 'bootcamp'; label: string }> = {
  'plink_1TuxBNPKWMZ26vxtKGFAVrhm': { type: 'private_class', label: 'Private Class 1h' },
  'plink_1TuxCDPKWMZ26vxtxTXtuzWP': { type: 'private_class', label: 'Private Class 3h' },
  'plink_1TuxDKPKWMZ26vxt46nfEPS9': { type: 'private_class', label: 'Private Class 5h' },
  'plink_1SH2gaPKWMZ26vxtbt3E4m3E': { type: 'bootcamp', label: 'Dominican Bootcamp' },
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
                <li><a href="https://axcentdance.com/_signup?email=${encodeURIComponent(email)}">Create your Student Portal account</a> — your pass, your weekly plan, sick-day declarations, and practice-room bookings, all in one place. Portal members are also the first to hear about member offers on future passes, workshops, and special events.</li>
              </ul>
              <p style="margin: 10px 0 0; font-size: 0.9em; color: #555;">
                Please create your account with this exact email address (${email}) — it is how the portal recognises your pass.
              </p>
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
