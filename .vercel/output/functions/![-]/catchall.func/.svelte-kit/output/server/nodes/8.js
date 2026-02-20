

export const index = 8;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/transactions/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/8.0h1KwkhH.js","_app/immutable/chunks/DSOgNidj.js","_app/immutable/chunks/BEA7QHMY.js","_app/immutable/chunks/D6YF6ztN.js","_app/immutable/chunks/BkX9Jbjf.js","_app/immutable/chunks/DBDV4xVz.js"];
export const stylesheets = ["_app/immutable/assets/8.oSwiSyoB.css"];
export const fonts = [];
