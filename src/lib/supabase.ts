import { createClient } from '@supabase/supabase-js';

// Runtime env vars that work in both Vercel and local dev
const getEnv = (name: string): string => {
  // Try import.meta.env first (Vite)
  if (typeof import.meta !== 'undefined' && import.meta.env) {
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

const url = getEnv('PUBLIC_SUPABASE_URL');
const key = getEnv('PUBLIC_SUPABASE_ANON_KEY');

if (!url || !key) {
  console.error('Missing Supabase env vars:', { url: !!url, key: !!key });
}

export const supabase = createClient(
  url || 'https://placeholder.supabase.co',
  key || 'placeholder'
);
