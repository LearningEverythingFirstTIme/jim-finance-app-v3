import * as universal from '../entries/pages/_layout.ts.js';

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export { universal };
export const universal_id = "src/routes/+layout.ts";
export const imports = ["_app/immutable/nodes/0.BtUif9Fp.js","_app/immutable/chunks/2ufbmRRR.js","_app/immutable/chunks/DfSwdc0w.js","_app/immutable/chunks/DSOgNidj.js","_app/immutable/chunks/CdmS54cz.js","_app/immutable/chunks/_ZlARY2_.js","_app/immutable/chunks/BTTWjJDS.js","_app/immutable/chunks/D6YF6ztN.js","_app/immutable/chunks/BEMRhe0s.js"];
export const stylesheets = ["_app/immutable/assets/0.DeSLWsH2.css"];
export const fonts = [];
