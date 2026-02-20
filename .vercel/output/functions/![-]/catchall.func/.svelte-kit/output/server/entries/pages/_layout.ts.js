import { redirect } from "@sveltejs/kit";
import { s as supabase } from "../../chunks/supabase.js";
const load = async ({ url }) => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session && url.pathname !== "/login") {
      throw redirect(302, "/login");
    }
    return { session };
  } catch (err) {
    if (url.pathname !== "/login") {
      throw redirect(302, "/login");
    }
    return { session: null };
  }
};
export {
  load
};
