// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import Stripe from 'https://esm.sh/stripe@11.1.0?target=deno'

console.log("Stripe Webhook Handler Started")

serve(async (req) => {
  const signature = req.headers.get('Stripe-Signature')

  // 1. Verify Request comes from Stripe
  if (!signature) {
    return new Response("No signature", { status: 400 })
  }

  const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY') ?? '', {
    apiVersion: '2022-11-15',
    httpClient: Stripe.createFetchHttpClient(),
  })

  // Read the body as text for verification
  const body = await req.text()
  let event

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      Deno.env.get('STRIPE_WEBHOOK_SECRET') ?? ''
    )
  } catch (err) {
    console.error(`Webhook signature verification failed: ${err.message}`)
    return new Response(err.message, { status: 400 })
  }

  // 2. Handle the Event
  if (event.type === 'checkout.session.completed') {
    const session = event.data.object
    const customerEmail = session.customer_details?.email
    // You can also get custom fields if you added them in Stripe Checkout
    // const customDate = session.custom_fields ... 

    console.log(`Processing payment for: ${customerEmail}`)

    if (customerEmail) {
      // Initialize Supabase Admin Client
      const supabaseAdmin = createClient(
        Deno.env.get('SUPABASE_URL') ?? '',
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
      )

      // 3. Find User ID
      // We search the public profiles (or auth via admin API if you prefer)
      // Note: This requires the user to have registered/logged in with this email already.
      // If they haven't registered, we might create a 'pending' record or just log it.

      // Let's try to find their Auth ID
      // Using listUsers is expensive, better to query a public table or use a specific RPC.
      // For now, let's assume we have a 'profiles' table or we can query registrations.

      // OPTION A: Search 'registrations' table (since we set that up earlier)
      // OPTION B: Search 'auth.users' (requires specific permissions)

      // Let's try to query the 'registrations' table we made in Phase 0
      const { data: userRecord, error: userError } = await supabaseAdmin
        .from('registrations')
        .select('id, email') // We might not have the AUTH id here if they only filled the form but didn't sign up to portal
        .eq('email', customerEmail)
        .single()

      // Ideally we want the AUTH ID for the Portal. 
      // If they don't have an account, we can't link it to the Portal yet.
      // But we CAN create the pass record and link it later when they sign up?
      // Or we just insert into 'user_passes' and look up the ID from auth.users via RPC?

      // Simplified Logic: We assume they ARE registered in Auth for the Portal to work.
      // We'll use a Supabase Admin function to look up user by email if possible, 
      // OR just wait for them to claim it. 

      // Better approach for MVP: 
      // Insert into 'user_passes'. If we don't know the UUID, we might fail.
      // Let's try to get the UUID from the profiles table (if you created one in Phase 1 plan? No, we skipped that).

      // FALLBACK: We will assume we can query `auth.users`. 
      // Supabase Edge Functions don't have direct access to `auth.users` via standard client unless we use the Admin API correctly.

      const { data: { users }, error: authError } = await supabaseAdmin.auth.admin.listUsers()
      const user = users.find(u => u.email === customerEmail)

      // 5. Send Welcome Email via Resend
      await sendWelcomeEmail(customerEmail, session.customer_details?.name || 'Dancer');

      if (user) {
        // 4. Create Pass (Existing Logic)
        const { error: insertError } = await supabaseAdmin
          .from('user_passes')
          .insert({
            user_id: user.id,
            package_name: 'Bachata 8-Week Pass', // Placeholder
            start_date: new Date().toISOString(),
            status: 'active'
          })

        if (insertError) {
          console.error('Error creating pass:', insertError)
        } else {
          console.log(`Pass created for user ${user.id}`)
        }
      }
    }
  }

  return new Response("Received", { status: 200 })
})

async function sendWelcomeEmail(email: string, name: string) {
  const RESEND_API_KEY = 're_GYPUGxYZ_Luc2qMfSJ6BA2g6YwQL1YPoy'; // User provided key

  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${RESEND_API_KEY}`
      },
      body: JSON.stringify({
        from: 'AXcent Dance <info@axcentdance.com>', // Requires Domain Verification in Resend
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
                <li>Check the <a href="https://axcentdance.com/schedule.html">Schedule</a> for your class times.</li>
                <li>Visit the <a href="https://axcentdance.com/portal.html">Student Portal</a> to manage your pass.</li>
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
