import { c as create_ssr_component, b as subscribe, e as each, d as add_attribute, f as escape } from "../../chunks/ssr.js";
import { p as page } from "../../chunks/stores.js";
const Layout = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let currentPath;
  let $page, $$unsubscribe_page;
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  const navItems = [
    {
      path: "/",
      label: "Home",
      icon: "📊"
    },
    {
      path: "/add",
      label: "Add",
      icon: "➕"
    },
    {
      path: "/transactions",
      label: "History",
      icon: "📋"
    },
    {
      path: "/bills",
      label: "Bills",
      icon: "🔄"
    },
    {
      path: "/import",
      label: "Import",
      icon: "📁"
    },
    {
      path: "/reports",
      label: "Reports",
      icon: "📈"
    }
  ];
  currentPath = $page.url.pathname;
  $$unsubscribe_page();
  return `<div class="app">${slots.default ? slots.default({}) : ``} <nav class="bottom-nav">${each(navItems, (item) => {
    return `<a${add_attribute("href", item.path, 0)} class="${[
      "nav-item",
      currentPath === item.path || item.path !== "/" && currentPath.startsWith(item.path) ? "active" : ""
    ].join(" ").trim()}"><span class="nav-icon">${escape(item.icon)}</span> ${escape(item.label)} </a>`;
  })}</nav></div>`;
});
export {
  Layout as default
};
