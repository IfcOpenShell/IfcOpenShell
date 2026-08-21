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
// Fallback root: the ifcviewer-web source dir holds sample.ifcview (which is
// embedded in the wasm, not copied into build-web). Lets the remote-backend
// test fetch http://localhost/sample.ifcview over real HTTP Range.
const SRC = path.resolve(__dirname, '..');

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
    // ?delay=<ms> stalls every response for this URL, HEAD and Range alike.
    // Load order across federated models is decided by whichever model's
    // async read chain finishes first, so a test that wants a specific
    // interleaving has to be able to make one source slower than another.
    const delay = Number(url.searchParams.get('delay') || 0);
    if (delay > 0) await new Promise((r) => setTimeout(r, delay));
    if (p === '/') p = '/IfcViewerWeb.html';
    const inRoot = path.join(ROOT, p);
    const inSrc  = path.join(SRC, p);
    // Contain to one of the two allowed roots.
    if (!inRoot.startsWith(ROOT) && !inSrc.startsWith(SRC)) { res.writeHead(403).end(); return; }
    let body;
    try { body = await readFile(inRoot); }
    catch { body = await readFile(inSrc); }   // fall back to the source dir
    const ctype = MIME[path.extname(p)] || 'application/octet-stream';

    // HEAD: headers only — lets the remote backend resolve total size.
    if (req.method === 'HEAD') {
      res.writeHead(200, {
        'Content-Type': ctype,
        'Content-Length': body.length,
        'Accept-Ranges': 'bytes',
      });
      res.end();
      return;
    }

    // Range: serve 206 partial content so the HTTP-Range backend is exercised
    // exactly as a real Accept-Ranges host would (handles bytes=a-b and a-).
    const range = req.headers['range'];
    const m = range && /^bytes=(\d*)-(\d*)$/.exec(range.trim());
    if (m) {
      let start = m[1] === '' ? undefined : parseInt(m[1], 10);
      let end   = m[2] === '' ? undefined : parseInt(m[2], 10);
      if (start === undefined) { start = body.length - end; end = body.length - 1; }  // bytes=-N
      if (end === undefined || end > body.length - 1) end = body.length - 1;            // bytes=a-
      if (Number.isNaN(start) || start > end) { res.writeHead(416).end(); return; }
      const slice = body.subarray(start, end + 1);
      res.writeHead(206, {
        'Content-Type': ctype,
        'Content-Range': `bytes ${start}-${end}/${body.length}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': slice.length,
      });
      res.end(slice);
      return;
    }

    res.writeHead(200, { 'Content-Type': ctype, 'Accept-Ranges': 'bytes' });
    res.end(body);
  } catch {
    res.writeHead(404).end('not found');
  }
}).listen(PORT, () => console.log(`serving ${ROOT} on http://localhost:${PORT}`));
