

export const index = 8;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/transactions/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/8.CBIxL0hg.js","_app/immutable/chunks/DSOgNidj.js","_app/immutable/chunks/BTTWjJDS.js","_app/immutable/chunks/D6YF6ztN.js","_app/immutable/chunks/BlK5NUL5.js","_app/immutable/chunks/_ZlARY2_.js"];
export const stylesheets = ["_app/immutable/assets/8.C-ls1_wy.css"];
export const fonts = [];
