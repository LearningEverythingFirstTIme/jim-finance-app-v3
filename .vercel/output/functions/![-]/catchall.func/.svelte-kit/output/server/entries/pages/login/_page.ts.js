import { redirect } from "@sveltejs/kit";
import { s as supabase } from "../../../chunks/supabase.js";
const load = async () => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session) {
    throw redirect(302, "/");
  }
  return {};
};
export {
  load
};
