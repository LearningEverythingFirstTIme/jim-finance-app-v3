import { redirect } from "@sveltejs/kit";
import { s as supabase } from "../../chunks/supabase.js";
const load = async ({ url }) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session && url.pathname !== "/login") {
    throw redirect(302, "/login");
  }
  return { session };
};
export {
  load
};
