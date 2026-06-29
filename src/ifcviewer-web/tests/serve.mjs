// Minimal static file server for the Emscripten build output. WebGPU
// needs a real http(s) origin (not file://), so the smoke test serves
// the build-web directory over localhost. No COOP/COEP headers yet —
// pthreads are off in the current web build (that's task #47).
//
// Serve dir resolution: $WEB_BUILD_DIR if set, else the repo's build-web.
import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = process.env.WEB_BUILD_DIR
  ? path.resolve(process.env.WEB_BUILD_DIR)
  : path.resolve(__dirname, '../../../build-web');
const PORT = Number(process.env.PORT || 8124);

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'text/javascript; charset=utf-8',
  '.mjs':  'text/javascript; charset=utf-8',
  '.wasm': 'application/wasm',
  '.ifcview': 'application/octet-stream',
};

http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    let p = decodeURIComponent(url.pathname);
    if (p === '/') p = '/IfcViewerWeb.html';
    const file = path.join(ROOT, p);
    // Contain to ROOT.
    if (!file.startsWith(ROOT)) { res.writeHead(403).end(); return; }
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type': MIME[path.extname(file)] || 'application/octet-stream' });
    res.end(body);
  } catch {
    res.writeHead(404).end('not found');
  }
}).listen(PORT, () => console.log(`serving ${ROOT} on http://localhost:${PORT}`));
