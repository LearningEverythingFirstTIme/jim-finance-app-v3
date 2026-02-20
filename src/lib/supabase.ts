import { createClient } from '@supabase/supabase-js';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';

// Fallback for build time when env vars might not be injected yet
const url = PUBLIC_SUPABASE_URL || '';
const key = PUBLIC_SUPABASE_ANON_KEY || '';

if (!url || !key) {
  console.warn('Supabase credentials not available - this is expected during build');
}

export const supabase = createClient(
  url || 'https://placeholder.supabase.co',
  key || 'placeholder-key'
);
