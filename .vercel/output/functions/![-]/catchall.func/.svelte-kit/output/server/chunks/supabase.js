import { createClient } from "@supabase/supabase-js";
const PUBLIC_SUPABASE_URL = "https://qqwnnvoahcsrffacafig.supabase.co";
const PUBLIC_SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxd25udm9haGNzcmZmYWNhZmlnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEzNTMyNjMsImV4cCI6MjA4NjkyOTI2M30.7OfMaGSLbvMNFOoT2fGB1DhiojKWO6R1Uoo1N8PTAIE";
const supabase = createClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY);
export {
  supabase as s
};
