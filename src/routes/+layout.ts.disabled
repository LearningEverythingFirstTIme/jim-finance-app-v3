import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';
import { supabase } from '$lib/supabase';

export const load: LayoutLoad = async ({ url }) => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session && url.pathname !== '/login') {
      throw redirect(302, '/login');
    }
    
    return { session };
  } catch (err) {
    // If Supabase fails (e.g., during build or bad creds), redirect to login
    if (url.pathname !== '/login') {
      throw redirect(302, '/login');
    }
    return { session: null };
  }
};
