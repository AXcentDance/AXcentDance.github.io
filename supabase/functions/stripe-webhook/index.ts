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
