import { createClient } from "@supabase/supabase-js";
import { b as browser } from "./false.js";
let url = "";
let key = "";
{
  url = process.env.VITE_SUPABASE_URL || process.env.PUBLIC_SUPABASE_URL || "";
  key = process.env.VITE_SUPABASE_ANON_KEY || process.env.PUBLIC_SUPABASE_ANON_KEY || "";
}
console.log("Supabase config:", { url: url?.slice(0, 20), key: key?.slice(0, 10), browser });
if (!url || !key) {
  console.error("Missing Supabase env vars");
}
const supabase = createClient(
  url || "https://placeholder.supabase.co",
  key || "placeholder"
);
export {
  supabase as s
};
