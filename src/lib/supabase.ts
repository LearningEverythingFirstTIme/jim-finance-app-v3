import { createClient } from '@supabase/supabase-js';
import { browser } from '$app/environment';

// For SvelteKit + Vite, we need to handle SSR vs browser differently
let url = '';
let key = '';

if (browser) {
  // In browser, use import.meta.env (Vite exposes these)
  url = import.meta.env.VITE_SUPABASE_URL || '';
  key = import.meta.env.VITE_SUPABASE_ANON_KEY || '';
} else {
  // On server during SSR, use process.env
  url = process.env.VITE_SUPABASE_URL || process.env.PUBLIC_SUPABASE_URL || '';
  key = process.env.VITE_SUPABASE_ANON_KEY || process.env.PUBLIC_SUPABASE_ANON_KEY || '';
}

console.log('Supabase config:', { url: url?.slice(0, 20), key: key?.slice(0, 10), browser });

if (!url || !key) {
  console.error('Missing Supabase env vars');
}

export const supabase = createClient(
  url || 'https://placeholder.supabase.co',
  key || 'placeholder'
);
