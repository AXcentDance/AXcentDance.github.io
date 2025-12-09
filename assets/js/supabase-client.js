
// Access global Supabase client (injected via script tag in HTML)
const { createClient } = window.supabase;

const SUPABASE_URL = 'https://rniyeykdljnkxsmvbppk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJuaXlleWtkbGpua3hzbXZicHBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzMDQwMjMsImV4cCI6MjA4MDg4MDAyM30.SO3fW_w9LC3R-aIA8lgSB04sRqc9io6WJf_lu6hzcIE';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

