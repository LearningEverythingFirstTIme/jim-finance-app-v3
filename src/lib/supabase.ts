import { createClient } from '@supabase/supabase-js';

// Support both Vite (dev) and Node (production) env vars
const supabaseUrl = typeof process !== 'undefined' && process.env.SUPABASE_URL 
  ? process.env.SUPABASE_URL 
  : import.meta.env?.VITE_SUPABASE_URL;

const supabaseKey = typeof process !== 'undefined' && process.env.SUPABASE_ANON_KEY 
  ? process.env.SUPABASE_ANON_KEY 
  : import.meta.env?.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('Missing Supabase environment variables. URL:', supabaseUrl, 'Key exists:', !!supabaseKey);
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseKey);
