// Shared Supabase client for the student portal pages.
// Requires the Supabase JS CDN script to be loaded first:
//   <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
// The anon key is public by design; data access is enforced by RLS policies.
const { createClient } = window.supabase;

const SUPABASE_URL = 'https://jwravnvytkmsvqoqkmwb.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3cmF2bnZ5dGttc3Zxb3FrbXdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM3NjU1MTIsImV4cCI6MjA5OTM0MTUxMn0.t4waGFmjD2hDQkGOhYg8rPt1rtf4iyRyTIC6T5KsFag';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
