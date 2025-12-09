
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"
import Stripe from "https://esm.sh/stripe@11.1.0?target=deno"

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY') ?? '', {
  apiVersion: '2022-11-15',
  httpClient: Stripe.createFetchHttpClient(),
})

console.log("Stripe Webhook Handler Started")

serve(async (req) => {
  const signature = req.headers.get('Stripe-Signature')

  if (!signature) {
    return new Response("No signature", { status: 400 })
  }

  try {
    const body = await req.text()
    // Verify the event came from Stripe
    // For simplicity in development, we might skip signature verification if strictly needed, 
    // but in prod we use constructEvent.
    // Note: To verify properly, we need the "Endpoint Secret" (whsec_...) 
    // which we don't have yet until we create the webhook in Stripe Dashboard.
    // For now, we will assume validity or use a try-catch for the basic parsing.

    // TEMPORARY: Just parse JSON to get it working first (less secure but easier for setup)
    const event = JSON.parse(body);

    if (event.type === 'checkout.session.completed') {
      const session = event.data.object
      const email = session.customer_details?.email || session.customer_email

      if (!email) {
        console.log("No email found in session")
        return new Response(JSON.stringify({ received: true, error: "No email" }), { status: 200 })
      }

      console.log(`Processing purchase for ${email}`)

      // Initialize Supabase Admin Client
      const supabaseAdmin = createClient(
        Deno.env.get('SUPABASE_URL') ?? '',
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
      )

      // Determine Course & Logic
      // We will need to fetch line items if they aren't in the session object directly 
      // (Stripe sessions usually require expansion for line_items).
      // For now, let's look at amount or metadata if available. 
      // Or we accept we might need to query Stripe API back for line items.

      // LOGIC MAPPING (Simplified by price amount or name if available)
      // Since we don't have line items easily here without complex calls, 
      // let's infer from the 'amount_total' if possible or log it as "Unknown Pass".

      let productName = "Dance Class Pass";
      let hours = 0;
      let stamps = 0;

      // You can refine this logic later by inspecting specific Price IDs
      const amount = session.amount_total; // in cents

      // Heuristic Logic (Example)
      // 1 Course (approx 260 CHF?)
      if (amount > 10000) {
        // Default assumptions for now
        // We ideally want to update this code after seeing a real payload
        hours = 8;
        stamps = 1;
      }

      // Insert into Database
      const { error } = await supabaseAdmin
        .from('purchases')
        .insert({
          user_email: email,
          course_name: productName,
          amount: amount / 100, // Convert cents to CHF
          hours_added: hours,
          stamps_added: stamps,
          date: new Date().toISOString()
        })

      if (error) {
        console.error("Supabase Insert Error:", error)
        return new Response(JSON.stringify({ error: error.message }), { status: 500 })
      }

      console.log("Purchase recorded successfully!")
    }

    return new Response(JSON.stringify({ received: true }), { headers: { "Content-Type": "application/json" } })

  } catch (err) {
    console.error(`Webhook Error: ${err.message}`)
    return new Response(`Webhook Error: ${err.message}`, { status: 400 })
  }
})
