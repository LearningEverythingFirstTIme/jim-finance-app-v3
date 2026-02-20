import { c as create_ssr_component, d as add_attribute, f as escape } from "../../../chunks/ssr.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
import "../../../chunks/supabase.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let password = "";
  return `${$$result.head += `<!-- HEAD_svelte-19iwguq_START -->${$$result.title = `<title>Sign In - Jim&#39;s Finance</title>`, ""}<!-- HEAD_svelte-19iwguq_END -->`, ""} <div class="login-page"><div class="login-container animate-fade-in"><div class="login-header" data-svelte-h="svelte-ozyzfa"><div class="logo">💰</div> <h1>Jim&#39;s Finance</h1> <p>Enter your password to continue</p></div> ${``} <form class="login-form"><div class="form-group"><label for="password" data-svelte-h="svelte-pepa0a">Password</label> <input id="password" type="password" class="input" placeholder="••••••••" required${add_attribute("value", password, 0)}></div> <button type="submit" class="btn btn-primary btn-lg" ${""}>${escape("Sign In")}</button></form></div></div>`;
});
export {
  Page as default
};
