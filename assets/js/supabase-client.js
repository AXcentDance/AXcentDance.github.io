
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'

// Configuration from User
const SUPABASE_URL = 'https://rniyeykdljnkxsmvbppk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJuaXlleWtkbGpua3hzbXZicHBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzMDQwMjMsImV4cCI6MjA4MDg4MDAyM30.SO3fW_w9LC3R-aIA8lgSB04sRqc9io6WJf_lu6hzcIE';

// Initialize Client
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
