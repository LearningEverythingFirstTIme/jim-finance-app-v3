import { createClient } from '@supabase/supabase-js';

// Runtime env vars that work in both Vercel and local dev
const getEnv = (name: string): string => {
  // Try import.meta.env first (Vite) - Vite exposes env vars on import.meta.env
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    // Vite replaces import.meta.env.VAR_NAME at build time
    const val = import.meta.env[name];
    if (val) return val;
  }
  // Fallback to process.env (Node/SSR)
  if (typeof process !== 'undefined' && process.env) {
    const val = process.env[name];
    if (val) return val;
  }
  return '';
};

// Support both VITE_ and PUBLIC_ prefixes for compatibility
const url = getEnv('VITE_SUPABASE_URL') || getEnv('PUBLIC_SUPABASE_URL');
const key = getEnv('VITE_SUPABASE_ANON_KEY') || getEnv('PUBLIC_SUPABASE_ANON_KEY');

if (!url || !key || url === 'https://placeholder.supabase.co') {
  console.error('Missing Supabase env vars. URL:', url, 'Key exists:', !!key);
}

export const supabase = createClient(
  url || 'https://placeholder.supabase.co',
  key || 'placeholder'
);
