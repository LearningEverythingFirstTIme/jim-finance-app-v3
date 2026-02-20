import { createClient } from '@supabase/supabase-js';

// Vite replaces import.meta.env.VAR at build time
// We need to access them directly, not through a function
const url = import.meta.env.VITE_SUPABASE_URL || import.meta.env.PUBLIC_SUPABASE_URL || '';
const key = import.meta.env.VITE_SUPABASE_ANON_KEY || import.meta.env.PUBLIC_SUPABASE_ANON_KEY || '';

if (!url || !key) {
  console.error('Missing Supabase env vars. URL exists:', !!url, 'Key exists:', !!key);
}

export const supabase = createClient(
  url || 'https://placeholder.supabase.co',
  key || 'placeholder'
);
