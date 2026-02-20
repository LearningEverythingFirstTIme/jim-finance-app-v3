import * as universal from '../entries/pages/_layout.ts.js';

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export { universal };
export const universal_id = "src/routes/+layout.ts";
export const imports = ["_app/immutable/nodes/0.BUdKklXM.js","_app/immutable/chunks/-UMntKAZ.js","_app/immutable/chunks/D9W0EZNd.js","_app/immutable/chunks/DSOgNidj.js","_app/immutable/chunks/CGYUU-3_.js","_app/immutable/chunks/DBDV4xVz.js","_app/immutable/chunks/BEA7QHMY.js","_app/immutable/chunks/D6YF6ztN.js","_app/immutable/chunks/50CvyOTN.js"];
export const stylesheets = ["_app/immutable/assets/0.CNIKQKR0.css"];
export const fonts = [];
