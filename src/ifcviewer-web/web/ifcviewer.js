// ifcviewer.js — a small JavaScript integration layer over the Emscripten
// module (IfcViewerWeb.js). Load this AFTER IfcViewerWeb.js, which defines the
// global `createIfcViewer` factory.
//
//   <script src="IfcViewerWeb.js"></script>
//   <script src="ifcviewer.js"></script>
//   <script>
//     const viewer = await IfcViewer.create({ canvas: myCanvas,
//                                             sidecarFormatVersion: 19,
//                                             navPreset: 'blender' });
//     await viewer.ready;                       // GPU app is live
//     await viewer.addFile(file, { replace: true });
//     await viewer.addUrl('/model.ifcview');    // appends (federation)
//
//     const objects = await viewer.getObjects();  // [{objectId, guid, name, type, model, sourceId}]
//     viewer.setSelection(['3vB2YO$MX4xv5uCqZZG05x']);
//     viewer.setColor(objects.filter(o => o.type === 'IfcWall'), '#ff8800');
//     viewer.setCamera({ yaw: 45, pitch: 30 });
//     viewer.setNavPreset('rhino');             // or switch schemes later
//     viewer.upsertGrid({ id: 'base', plane: 'xy', spacing: 1, divisions: 50 });
//     viewer.setOriginAxes(1000);               // metres either side of the origin
//   </script>
//
// The canvas element MUST have id="viewer-canvas" — the wasm side hard-codes
// that selector for its WebGPU surface and input handlers.
//
// Model identity. addFile/addUrl return a source id: the handle for that model,
// minted the moment it is registered and stable for the session. Objects come
// back tagged with both their `sourceId` and a `model` index (the model's slot
// in load order). Map an object to the file it came from through the source id
// — the index is a POSITION, so it shifts down if an earlier model fails to
// load, and a host keying its own list off it then attributes objects to the
// wrong file.
//
// Object identity. Everything the scripting API takes or returns is keyed by
// `objectId`: a u32 the renderer assigns, unique across the federation but only
// meaningful for this session. IFC GlobalIds are the stable identity, and every
// id-taking call also accepts them — resolved through the element table that
// getObjects() fetches. Because that fetch is lazy (per model, so first paint
// never waits on it), a GUID can only be resolved once getObjects() has
// resolved at least once; passing one before that throws rather than silently
// selecting nothing.
(function (global) {
  'use strict';

  // .ifcview head: magic, format version, endian. Native-endian; the web
  // build and the baker are both little-endian. Must match IfcViewFormat.h.
  const IFCVIEW_MAGIC  = 0x49465657;  // "IFVW"
  const IFCVIEW_ENDIAN = 0x01020304;

  // Metres per federation unit. Matches the units the scripting page offers.
  // Anything else is treated as metres; the composed matrix on the wasm side
  // is what the survey marker actually uses.
  function federationUnitToMeters(u) {
    const name = ((u && u.name) || 'METRE').toUpperCase();
    const prefix = ((u && u.prefix) || '').toUpperCase();
    if (name === 'FOOT' || name === 'FEET') return 0.3048;
    if (name === 'INCH' || name === 'INCHES') return 0.0254;
    if (name === 'METRE' || name === 'METER') {
      if (prefix === 'MILLI') return 0.001;
      if (prefix === 'CENTI') return 0.01;
      if (prefix === 'DECI') return 0.1;
      if (prefix === 'KILO') return 1000;
      return 1;
    }
    return 1;
  }

  // Where world 0, 0, 0 is drawn, in viewer metres: Rz · (0 − xyz), the same
  // matrix composeFederatedFalseOrigin builds. The false origin itself is
  // drawn at viewer 0, 0, 0.
  function worldOriginInViewer(origin, unit) {
    const s = federationUnitToMeters(unit);
    const xyz = (origin && origin.xyz) || [0, 0, 0];
    const a = ((origin && origin.rzDeg) || 0) * Math.PI / 180;
    const c = Math.cos(a), n = Math.sin(a);
    const x = -xyz[0] * s, y = -xyz[1] * s;
    return [c * x - n * y, n * x + c * y, -xyz[2] * s];
  }

  function federationUnitLabel(u) {
    const name = (u && u.name) || 'METRE';
    const prefix = (u && u.prefix) || '';
    if (name === 'METRE' && prefix === '') return 'm';
    if (name === 'METRE' && prefix === 'MILLI') return 'mm';
    if (name === 'METRE' && prefix === 'CENTI') return 'cm';
    if (name === 'METRE' && prefix === 'KILO') return 'km';
    if (name === 'foot' || name === 'FEET') return 'ft';
    if (name === 'inch') return 'in';
    return (prefix ? prefix + ' ' : '') + name;
  }

  function fmtCoord(v) {
    if (!isFinite(v)) return '—';
    const abs = Math.abs(v);
    const digits = abs >= 1000 ? 2 : abs >= 1 ? 3 : 4;
    const negative = v < 0;
    const parts = Math.abs(v).toFixed(digits).split('.');
    const grouped = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    return (negative ? '−' : '') + grouped + (parts[1] ? '.' + parts[1] : '');
  }

  function originShifted(xyz) {
    return Math.hypot(xyz[0], xyz[1], xyz[2]) > 1e-3;
  }

  function originMoved(a, b) {
    return Math.hypot(b.xyz[0] - a.xyz[0], b.xyz[1] - a.xyz[1], b.xyz[2] - a.xyz[2]) > 1e-3
      || Math.abs(b.rzDeg - a.rzDeg) > 1e-3
      || b.explicit !== a.explicit;
  }

  // Same orbit projection as ViewportCore::buildViewProj, for builds that
  // do not yet export ifcv_project_world_c. FOV / clip planes match the
  // core defaults (45°, 0.1…10000).
  function projectWorldFromCamera(cam, canvas, xyz) {
    if (!cam || !canvas) return null;
    const eye = cam.eye, target = cam.target;
    let fx = target[0] - eye[0], fy = target[1] - eye[1], fz = target[2] - eye[2];
    const fl = Math.hypot(fx, fy, fz) || 1;
    fx /= fl; fy /= fl; fz /= fl;
    const up = Math.abs(cam.pitch) >= 89 ? [0, 1, 0] : [0, 0, 1];
    let sx = fy * up[2] - fz * up[1];
    let sy = fz * up[0] - fx * up[2];
    let sz = fx * up[1] - fy * up[0];
    const sl = Math.hypot(sx, sy, sz) || 1;
    sx /= sl; sy /= sl; sz /= sl;
    const ux = sy * fz - sz * fy;
    const uy = sz * fx - sx * fz;
    const uz = sx * fy - sy * fx;
    const vx = sx * xyz[0] + sy * xyz[1] + sz * xyz[2] - (sx * eye[0] + sy * eye[1] + sz * eye[2]);
    const vy = ux * xyz[0] + uy * xyz[1] + uz * xyz[2] - (ux * eye[0] + uy * eye[1] + uz * eye[2]);
    const vz = -fx * xyz[0] - fy * xyz[1] - fz * xyz[2] + (fx * eye[0] + fy * eye[1] + fz * eye[2]);
    const rect = canvas.getBoundingClientRect();
    const cssW = rect.width || canvas.clientWidth || 1;
    const cssH = rect.height || canvas.clientHeight || 1;
    const aspect = cssW / cssH;
    const t = Math.tan(45 * Math.PI / 360);
    let cx, cy, cw;
    if (cam.ortho) {
      const halfH = cam.distance * t;
      const halfW = halfH * aspect;
      cx = vx / halfW;
      cy = vy / halfH;
      cw = 1;
    } else {
      cx = vx / (aspect * t);
      cy = vy / t;
      cw = -vz;
    }
    if (cw <= 1e-4) return null;
    const ndcX = cx / cw;
    const ndcY = cy / cw;
    return {
      x: (ndcX * 0.5 + 0.5) * cssW,
      y: (1 - (ndcY * 0.5 + 0.5)) * cssH,
    };
  }

  // First 12 bytes of a File/Blob or a URL (ranged). Network failure throws
  // a plain Error; a header that is present but not the expected sidecar
  // format throws with .sidecarFormat set so the caller can tell the two apart.
  async function readSidecarHead(source) {
    let buf;
    if (typeof source === 'string') {
      let res;
      try {
        res = await fetch(source, { headers: { Range: 'bytes=0-11' } });
      } catch (err) {
        throw new Error('could not read .ifcview header: ' + (err && err.message || err));
      }
      if (res.status !== 206 && res.status !== 200) {
        throw new Error('could not read .ifcview header (' + res.status + ')');
      }
      buf = await res.arrayBuffer();
    } else if (source && typeof source.slice === 'function') {
      buf = await source.slice(0, 12).arrayBuffer();
    } else {
      const err = new Error('not an .ifcview file');
      err.sidecarFormat = true;
      throw err;
    }
    if (buf.byteLength < 12) {
      const err = new Error('not an .ifcview file');
      err.sidecarFormat = true;
      throw err;
    }
    const view = new DataView(buf);
    return {
      magic:   view.getUint32(0, true),
      version: view.getUint32(4, true),
      endian:  view.getUint32(8, true),
    };
  }

  function assertSidecarHead(head, expected) {
    const reject = (message) => {
      const err = new Error(message);
      err.sidecarFormat = true;
      throw err;
    };
    if (head.magic !== IFCVIEW_MAGIC || head.endian !== IFCVIEW_ENDIAN) {
      reject('not an .ifcview file');
    }
    if (head.version !== expected) {
      reject('.ifcview sidecar format is v' + head.version +
             '; this page loads v' + expected);
    }
  }

  // Resolve a remote .ifcview's total size so the loader can bound its ranged
  // reads: HEAD Content-Length, falling back to a 0-0 Range's Content-Range.
  async function sizeUrl(url) {
    const head = await fetch(url, { method: 'HEAD' });
    const len = head.ok ? parseInt(head.headers.get('Content-Length') || '0', 10) : 0;
    if (len > 0) return len;
    const probe = await fetch(url, { headers: { Range: 'bytes=0-0' } });
    const cr = probe.headers.get('Content-Range'); // "bytes 0-0/12345"
    return cr ? parseInt(cr.split('/')[1] || '0', 10) : 0;
  }

  // ---- OPFS model cache ------------------------------------------------------
  //
  // addUrl(url, {cache: true}) keeps a local copy of the .ifcview in the
  // Origin Private File System, filled FROM THE VIEWER'S OWN RANGED READS —
  // no second download, and only the bytes the camera actually needed.
  // (Browsers do not populate their HTTP cache from ranged fetches: measured
  // 0 of 78 range requests served from cache even with a strong ETag.)
  //
  // Entries are keyed by a hash of the URL and validated by ETag (falling
  // back to Last-Modified + size); a byte-span ledger records which ranges
  // are really on disk, so a partial copy is never mistaken for a whole one —
  // a read is served locally only when its span is fully covered. On the next
  // visit a complete validated copy loads with zero geometry traffic; if the
  // server is unreachable, the newest complete copy is used as-is (offline).
  //
  // Writes go through a dedicated worker holding a FileSystemSyncAccessHandle:
  // positional writes with no copy-on-open (createWritable({keepExistingData})
  // copies the whole existing file into a swap file per open — quadratic as
  // the cache fills), and the handle's exclusive lock makes a second tab fall
  // back to plain network instead of corrupting the entry. Browsers without
  // sync access handles just never cache — behaviour is exactly as without
  // the flag.
  const CACHE_DIR = 'ifcviewer-cache';

  const cacheWorkerSource = `
    const handles = new Map();
    onmessage = async (e) => {
      const { id, op, name, pos, data, len } = e.data;
      const reply = (msg, transfer) => postMessage(Object.assign({ id }, msg), transfer || []);
      try {
        if (op === 'open') {
          const root = await navigator.storage.getDirectory();
          const dir = await root.getDirectoryHandle('${CACHE_DIR}', { create: true });
          const fh = await dir.getFileHandle(name, { create: true });
          handles.set(name, await fh.createSyncAccessHandle());
          reply({ ok: true, size: handles.get(name).getSize() });
        } else if (op === 'write') {
          handles.get(name).write(new Uint8Array(data), { at: pos });
          reply({ ok: true });
        } else if (op === 'read') {
          const buf = new Uint8Array(len);
          const n = handles.get(name).read(buf, { at: pos });
          reply({ ok: n === len, data: buf.buffer }, [buf.buffer]);
        } else if (op === 'close') {
          const h = handles.get(name);
          if (h) { h.flush(); h.close(); handles.delete(name); }
          reply({ ok: true });
        } else {
          reply({ ok: false, error: 'unknown op ' + op });
        }
      } catch (err) {
        reply({ ok: false, error: String((err && err.message) || err) });
      }
    };
  `;

  let cacheWorker = null;   // lazily created; false once known unusable
  let cacheMsgId = 0;
  const cachePending = new Map();
  function cacheCall(op, name, extra, transfer) {
    if (cacheWorker === false) return Promise.reject(new Error('no cache worker'));
    if (!cacheWorker) {
      try {
        cacheWorker = new Worker(URL.createObjectURL(
          new Blob([cacheWorkerSource], { type: 'text/javascript' })));
        cacheWorker.onmessage = (e) => {
          const pending = cachePending.get(e.data.id);
          if (!pending) return;
          cachePending.delete(e.data.id);
          if (e.data.ok) pending.resolve(e.data);
          else pending.reject(new Error(e.data.error || (op + ' failed')));
        };
      } catch (err) {
        cacheWorker = false;
        return Promise.reject(err);
      }
    }
    const id = ++cacheMsgId;
    return new Promise((resolve, reject) => {
      cachePending.set(id, { resolve: resolve, reject: reject });
      cacheWorker.postMessage(Object.assign({ id: id, op: op, name: name }, extra || {}),
                              transfer || []);
    });
  }

  async function cacheDirHandle(create) {
    const root = await navigator.storage.getDirectory();
    return root.getDirectoryHandle(CACHE_DIR, { create: !!create });
  }

  let persistAsked = false;
  async function openCacheDir() {
    try {
      const dir = await cacheDirHandle(true);
      // Without this a large cache is "best effort" and the browser may drop
      // it under disk pressure — invisibly, looking like the site being slow
      // again on the next visit.
      if (!persistAsked && navigator.storage.persist) {
        persistAsked = true;
        navigator.storage.persist().catch(() => {});
      }
      return dir;
    } catch (err) {
      return null;
    }
  }

  async function cacheEntryName(url, formatVersion) {
    const bytes = new TextEncoder().encode(String(formatVersion) + '\0' + url);
    const digest = await crypto.subtle.digest('SHA-256', bytes);
    return Array.from(new Uint8Array(digest).slice(0, 16))
      .map((b) => b.toString(16).padStart(2, '0')).join('');
  }

  // Sorted, merged, half-open [start, end) byte spans.
  function spansAdd(spans, start, end) {
    const out = [];
    let s0 = start, e0 = end;
    for (const [a, b] of spans) {
      if (b < s0 || a > e0) out.push([a, b]);
      else { s0 = Math.min(s0, a); e0 = Math.max(e0, b); }
    }
    out.push([s0, e0]);
    out.sort((x, y) => x[0] - y[0]);
    return out;
  }
  const spansCover = (spans, start, end) =>
    spans.some(([a, b]) => a <= start && b >= end);
  const spansBytes = (spans) => spans.reduce((sum, [a, b]) => sum + (b - a), 0);

  async function readCacheMeta(dir, name) {
    try {
      const fh = await dir.getFileHandle(name + '.meta');
      return JSON.parse(await (await fh.getFile()).text());
    } catch (err) {
      return null;
    }
  }
  // The meta file is tiny, so main-thread createWritable is fine here; only
  // the tab holding the data file's exclusive lock ever writes it.
  async function writeCacheMeta(dir, name, meta) {
    const fh = await dir.getFileHandle(name + '.meta', { create: true });
    const w = await fh.createWritable();
    await w.write(JSON.stringify(meta));
    await w.close();
  }
  async function removeCacheEntry(dir, name) {
    await dir.removeEntry(name).catch(() => {});
    await dir.removeEntry(name + '.meta').catch(() => {});
  }

  async function headValidators(url) {
    try {
      const res = await fetch(url, { method: 'HEAD' });
      if (!res.ok) return null;
      return {
        etag: res.headers.get('ETag') || null,
        lastModified: res.headers.get('Last-Modified') || null,
        size: parseInt(res.headers.get('Content-Length') || '0', 10) || 0,
      };
    } catch (err) {
      return null;    // offline, or CORS refused HEAD
    }
  }
  function validatorsMatch(meta, head) {
    if (meta.etag && head.etag) return meta.etag === head.etag;
    if (meta.lastModified && head.lastModified) {
      return meta.lastModified === head.lastModified && meta.size === head.size;
    }
    return false;
  }

  // A Blob-shaped source (`size` + `slice(a, b).arrayBuffer()`) backed by the
  // OPFS entry, filling from every ranged read that goes through it. The
  // wasm's read shim only ever calls those two members, so this passes for
  // the File it would get from a picked file.
  function fillingCacheSource(dir, name, url, meta) {
    let spans = meta.spans.slice();
    let dirtySince = 0;     // bytes written since the ledger was persisted
    let broken = false;     // a write failed (quota?): serve network, stop filling
    let complete = spansCover(spans, 0, meta.size);
    let writeChain = Promise.resolve();
    let lastForegroundRead = 0;   // performance.now() of the viewer's last read

    const persistLedger = () => {
      dirtySince = 0;
      return writeCacheMeta(dir, name, Object.assign({}, meta, { spans: spans }))
        .catch(() => {});
    };
    const finishIfComplete = () => {
      if (complete || !spansCover(spans, 0, meta.size)) return;
      complete = true;
      // Flush + release the lock; from here reads come off the closed file.
      writeChain = writeChain
        .then(() => cacheCall('close', name))
        .then(persistLedger)
        .catch(() => {});
    };

    const storeBytes = (start, stop, buf) => {
      if (broken || complete || buf.byteLength !== stop - start) return;
      const copy = buf.slice(0);
      writeChain = writeChain
        .then(() => cacheCall('write', name, { pos: start, data: copy }, [copy]))
        .then(() => {
          spans = spansAdd(spans, start, stop);
          dirtySince += stop - start;
          // Persist the ledger periodically — bytes on disk that the
          // ledger does not record are merely re-fetched next visit.
          if (dirtySince >= (4 << 20)) return persistLedger();
        })
        .then(finishIfComplete)
        .catch(() => { broken = true; });
    };

    // Background completion: streaming only reads what the camera needs, so
    // left alone the cache converges on the *viewed* bytes, not the file —
    // and a user cannot be expected to orbit every model into view to
    // finish it. Once the viewer has been quiet for a moment, fetch the
    // uncovered spans in order, one modest range at a time, yielding
    // whenever real reads resume so interactive streaming always wins.
    const IDLE_MS = 1500, STEP_BYTES = 8 << 20;
    let backgroundDone = false;
    async function backgroundFill() {
      while (!complete && !broken && !backgroundDone) {
        if (performance.now() - lastForegroundRead < IDLE_MS) {
          await new Promise((r) => setTimeout(r, IDLE_MS));
          continue;
        }
        // First gap not yet covered.
        let at = 0;
        for (const [a, b] of spans) { if (a > at) break; at = Math.max(at, b); }
        if (at >= meta.size) { finishIfComplete(); return; }
        let stop = Math.min(at + STEP_BYTES, meta.size);
        for (const [a] of spans) { if (a > at) { stop = Math.min(stop, a); break; } }
        try {
          const res = await fetch(url, {
            headers: { Range: 'bytes=' + at + '-' + (stop - 1) },
          });
          if (res.status !== 206 && res.status !== 200) return;   // server changed its mind
          let buf = await res.arrayBuffer();
          if (res.status === 200 && buf.byteLength > stop - at) buf = buf.slice(at, stop);
          storeBytes(at, stop, buf);
          await writeChain;
        } catch (err) {
          return;   // offline etc: the foreground path is affected too, stop quietly
        }
      }
    }
    setTimeout(backgroundFill, IDLE_MS);

    return {
      size: meta.size,
      stopBackgroundFill() { backgroundDone = true; },
      slice(start, end) {
        const stop = Math.min(end, meta.size);
        return {
          arrayBuffer: async () => {
            lastForegroundRead = performance.now();
            if (spansCover(spans, start, stop)) {
              if (complete) {
                const fh = await dir.getFileHandle(name);
                return (await fh.getFile()).slice(start, stop).arrayBuffer();
              }
              // Serialise behind the writes so a just-written range is
              // readable (sync-handle writes are visible to the same handle
              // immediately; ordering through the chain keeps it simple).
              return (writeChain = writeChain.then(() =>
                cacheCall('read', name, { pos: start, len: stop - start })
              )).then((r) => r.data);
            }
            const res = await fetch(url, {
              headers: { Range: 'bytes=' + start + '-' + (stop - 1) },
            });
            if (res.status !== 206 && res.status !== 200) {
              throw new Error('range fetch failed: ' + res.status);
            }
            let buf = await res.arrayBuffer();
            if (res.status === 200 && buf.byteLength > stop - start) {
              buf = buf.slice(start, stop);
            }
            storeBytes(start, stop, buf);
            return buf;
          },
        };
      },
    };
  }

  // Decide what to hand the loader for a cached URL:
  //   {file}    — a complete validated local copy (zero network)
  //   {source}  — a Blob-shaped self-filling source
  //   null      — cache unusable here (no OPFS / no validators / second tab):
  //               caller falls back to the plain URL path.
  async function cachedUrlSource(url, formatVersion) {
    if (!(crypto && crypto.subtle) || !(navigator.storage && navigator.storage.getDirectory)) {
      return null;
    }
    const head = await headValidators(url);
    const dir = await openCacheDir();
    if (!dir) return null;
    const name = await cacheEntryName(url, formatVersion);
    let meta = await readCacheMeta(dir, name);
    if (meta && meta.formatVersion !== formatVersion) {
      await removeCacheEntry(dir, name);
      meta = null;
    }

    const completeLocal = async (m) => {
      if (m.formatVersion !== formatVersion) return null;
      const fh = await dir.getFileHandle(name);
      const file = await fh.getFile();
      if (file.size !== m.size) return null;
      // A copy baked for another sidecar format must not be served, even
      // offline: the bytes are the wrong cache format for this page.
      try {
        assertSidecarHead(await readSidecarHead(file), formatVersion);
      } catch (err) {
        await removeCacheEntry(dir, name);
        return null;
      }
      return { file: file };
    };

    if (!head) {
      // Offline (or HEAD refused): a complete copy is better than nothing —
      // this is the offline story. Anything less falls back to the URL path,
      // which will fail the same way it always did.
      if (meta && spansCover(meta.spans, 0, meta.size)) return completeLocal(meta);
      return null;
    }
    if (!head.etag && !head.lastModified) return null;  // nothing to validate by
    if (!head.size) return null;

    if (meta && validatorsMatch(meta, head)) {
      if (spansCover(meta.spans, 0, meta.size)) {
        const local = await completeLocal(meta);
        if (local) return local;
        // completeLocal drops an entry whose header is the wrong format.
        meta = await readCacheMeta(dir, name);
      }
      // Partial copy of the still-current file: resume filling it.
    } else if (meta) {
      await removeCacheEntry(dir, name);      // server has a different file now
      meta = null;
    }

    const fresh = (!meta || !validatorsMatch(meta, head))
      ? { url: url, etag: head.etag, lastModified: head.lastModified,
          size: head.size, spans: [], formatVersion: formatVersion }
      : meta;
    try {
      await cacheCall('open', name);          // exclusive: a second tab lands in catch
    } catch (err) {
      return null;
    }
    await writeCacheMeta(dir, name, fresh).catch(() => {});
    return { source: fillingCacheSource(dir, name, url, fresh) };
  }

  // Mouse navigation schemes the wasm's classifyPress understands. Named so a
  // typo is an error here rather than a silent fall-back to blender in the core.
  const NAV_PRESETS = ['blender', 'rhino', 'revit', 'web'];

  // Pack a colour into the u32 the shader unpacks: 0xAABBGGRR. Accepts
  // '#rgb' / '#rrggbb' / '#rrggbbaa', or {r, g, b, a} with 0-255 channels
  // (alpha defaulting to opaque). An alpha of 0 is the "no override" sentinel
  // on the wasm side, so a fully transparent colour is a clear, not a colour —
  // hide the object instead if that is what you meant.
  function packColor(color) {
    if (color === null || color === undefined) return 0;
    let r, g, b, a = 255;
    if (typeof color === 'string') {
      let hex = color.replace(/^#/, '');
      if (hex.length === 3) hex = hex.split('').map(function (c) { return c + c; }).join('');
      if (hex.length !== 6 && hex.length !== 8) throw new Error('bad colour: ' + color);
      r = parseInt(hex.slice(0, 2), 16);
      g = parseInt(hex.slice(2, 4), 16);
      b = parseInt(hex.slice(4, 6), 16);
      if (hex.length === 8) a = parseInt(hex.slice(6, 8), 16);
    } else {
      r = color.r | 0; g = color.g | 0; b = color.b | 0;
      if (color.a !== undefined) a = color.a | 0;
    }
    const clamp = function (v) { return Math.max(0, Math.min(255, v | 0)); };
    return ((clamp(a) << 24) | (clamp(b) << 16) | (clamp(g) << 8) | clamp(r)) >>> 0;
  }

  // Line grids. plane: 'xy' | 'xz' | 'yz'. Colors are sRGB [0..1].
  // Both directions default to the same light grey. The renderer draws every
  // 10th line at this colour and the lines between them lighter.
  var GRID_PLANE_IDS = { xy: 0, xz: 1, yz: 2 };
  var GRID_COLOR = [0.42, 0.42, 0.42];
  var GRID_PLANE_AXIS_COLORS = {
    xy: { u: GRID_COLOR, v: GRID_COLOR },
    xz: { u: GRID_COLOR, v: GRID_COLOR },
    yz: { u: GRID_COLOR, v: GRID_COLOR },
  };
  var GRID_DEFAULT_COLOR = -1;
  var GRID_MAJOR_OPACITY = 0.55;
  var GRID_UPSERT_ARG_TYPES = [
    'string', 'number', 'number', 'number', 'number', 'number', 'number',
    'number', 'number', 'number', 'number', 'number', 'number', 'number', 'number',
  ];

  function normalizeGridDefinition(definition) {
    var plane = definition.plane || 'xy';
    var defaults = GRID_PLANE_AXIS_COLORS[plane] || GRID_PLANE_AXIS_COLORS.xy;
    var origin = definition.origin || [0, 0, 0];
    return {
      id: definition.id,
      plane: plane,
      origin: [origin[0] || 0, origin[1] || 0, origin[2] || 0],
      spacing: Math.max(0.001, definition.spacing || 1),
      divisions: Math.max(1, definition.divisions | 0 || 50),
      colorU: definition.colorU || defaults.u,
      colorV: definition.colorV || defaults.v,
      opacity: definition.opacity != null ? definition.opacity : GRID_MAJOR_OPACITY,
      visible: definition.visible !== false,
    };
  }

  function upsertGridWasm(Module, grid) {
    if (!Module._grid_upsert_c && typeof Module.ccall !== 'function') return;
    var u = grid.colorU || [GRID_DEFAULT_COLOR, GRID_DEFAULT_COLOR, GRID_DEFAULT_COLOR];
    var v = grid.colorV || [GRID_DEFAULT_COLOR, GRID_DEFAULT_COLOR, GRID_DEFAULT_COLOR];
    var args = [
      grid.id,
      grid.origin[0], grid.origin[1], grid.origin[2],
      GRID_PLANE_IDS[grid.plane] || 0,
      grid.spacing,
      grid.divisions,
      u[0], u[1], u[2],
      v[0], v[1], v[2],
      grid.opacity != null ? grid.opacity : GRID_MAJOR_OPACITY,
      grid.visible ? 1 : 0,
    ];
    // Direct wasm exports do not UTF-8 marshal JS strings — ccall is required for ids.
    if (typeof Module.ccall === 'function') {
      Module.ccall('grid_upsert_c', null, GRID_UPSERT_ARG_TYPES, args);
    } else {
      Module._grid_upsert_c.apply(Module, args);
    }
    if (Module._viewer_request_frame) Module._viewer_request_frame();
  }

  function removeGridWasm(Module, id) {
    if (typeof Module.ccall === 'function') {
      return Module.ccall('grid_remove_c', 'number', ['string'], [id]) !== 0;
    }
    if (!Module._grid_remove_c) return false;
    return Module._grid_remove_c(id) !== 0;
  }

  // Boot a viewer bound to `opts.canvas`. Resolves to the API object once the
  // wasm runtime is initialised; `api.ready` resolves once the GPU app is live.
  async function create(opts) {
    opts = opts || {};
    const sidecarFormatVersion = opts.sidecarFormatVersion;
    if (!Number.isInteger(sidecarFormatVersion) || sidecarFormatVersion < 1) {
      throw new Error('IfcViewer.create requires sidecarFormatVersion: the .ifcview ' +
        'sidecar format this page loads (IFCVIEW_VERSION in IfcViewFormat.h)');
    }
    const factory = opts.moduleFactory || global.createIfcViewer;
    if (typeof factory !== 'function') {
      throw new Error('createIfcViewer not found — load IfcViewerWeb.js first');
    }
    var gridRegistry = Object.create(null);

    const selectListeners = [];
    const selectionListeners = [];
    const modelLoadedListeners = [];
    const frameListeners = [];
    // Value space for the false origin and for a transform's b/pivot. The
    // wasm default is metres; setFederationUnit is the only writer.
    let federationUnit = { name: 'METRE', prefix: '' };
    // null until the first projectWorld: true once ifcv_project_world_c
    // answers, false when this wasm build does not export it.
    let projectWorldNative = null;
    let api = null;   // built below; the RAF loop only reads it after that
    let live = false;
    let resolveReady;
    const ready = new Promise(function (r) { resolveReady = r; });

    // Both built from the last getObjects(); null until then. objectIndex backs
    // GlobalId resolution (see the identity note at the top of the file);
    // objectsById puts the IFC identity back onto a selection read.
    let objectIndex = null;
    let objectsById = null;

    // The per-frame loop: poll for the app pointer (published once the GPU
    // device is ready), then drive the C tick. It is registered from
    // onRuntimeInitialized (a clean callback context) rather than after
    // `await factory(...)` — that Promise.then continuation is exactly the
    // nesting that stalls Dawn-web's device callback and leaves the GPU device
    // half-initialised (every buffer then reports "invalid"). Learned during
    // the original web bring-up; kept here deliberately.
    function startLoop(Module) {
      function tick() {
        if (Module._app_ptr && Module._raf_tick_c) {
          if (!live) {
            live = true;
            resolveReady(api);
            if (opts.onReady) opts.onReady(api);
          }
          Module._raf_tick_c(Module._app_ptr);
          for (let i = 0; i < frameListeners.length; i++) {
            try { frameListeners[i](api); } catch (e) { console.error(e); }
          }
          if (opts.onFrame) opts.onFrame(api);
        }
        requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }

    // Per-frame '[info] [frame] … fps …' heartbeat lines come from
    // ViewportCore.cpp (Log::info()) and fire every render tick. Silence
    // them by default; opt back in with { verboseFrames: true }.
    const verboseFrames = opts.verboseFrames === true;
    const defaultPrintErr = function (t) {
      if (!verboseFrames && typeof t === 'string' && t.startsWith('[info] [frame]')) return;
      console.warn(t);
    };

    const Module = await factory({
      canvas: opts.canvas,
      // Keep the runtime alive after main() returns so Dawn-web's async
      // adapter/device callbacks land (they set Module._app_ptr).
      noExitRuntime: true,
      print:    opts.print    || function (t) { console.log(t); },
      printErr: opts.printErr || defaultPrintErr,
      onRuntimeInitialized: function () { startLoop(this); },
    });

    // ---- wasm heap marshalling ---------------------------------------------
    //
    // Arrays cross the boundary as (pointer, count) into the wasm heap. Both
    // helpers own the malloc/free pair so no call site can leak one.

    // Copy `ids` into a scratch u32 buffer and hand (ptr, count) to `fn`.
    function withIdArray(ids, fn) {
      const n = ids.length;
      if (n === 0) return fn(0, 0);
      const ptr = Module._malloc(n * 4);
      try {
        Module.HEAPU32.set(Uint32Array.from(ids), ptr >>> 2);
        return fn(ptr, n);
      } finally {
        Module._free(ptr);
      }
    }

    // Run an "ask twice" getter: `fn(ptr, max)` fills at most `max` u32s and
    // returns the TOTAL count. Call it empty to size, then again to fill.
    function readIdArray(fn) {
      const total = fn(0, 0);
      if (total <= 0) return [];
      const ptr = Module._malloc(total * 4);
      try {
        fn(ptr, total);
        return Array.from(Module.HEAPU32.subarray(ptr >>> 2, (ptr >>> 2) + total));
      } finally {
        Module._free(ptr);
      }
    }

    // The one selection mutator: mode 0 replaces (an empty list clears), 1 adds,
    // 2 removes. Notifies listeners itself, so a programmatic change reaches
    // onSelectionChange through the same path a click does.
    function applySelection(x, mode) {
      withIdArray(resolveIds(x), function (ptr, n) {
        Module._ifcv_apply_selection_c(ptr, n, mode);
      });
      Module.__ifcvOnSelectionChange();
    }

    // Normalise whatever the caller passed into a flat array of objectIds.
    // Accepts a number, an IFC GlobalId string, an object with an `objectId`
    // or `guid` field (so an element straight out of getObjects() works), or
    // an array of any of those. null/undefined is an empty selection.
    function resolveIds(x) {
      if (x === null || x === undefined) return [];
      if (!Array.isArray(x)) x = [x];
      return x.map(function (item) {
        if (typeof item === 'number') return item >>> 0;
        if (item && typeof item === 'object') {
          if (typeof item.objectId === 'number') return item.objectId >>> 0;
          item = item.guid;
        }
        if (typeof item !== 'string') throw new Error('not an objectId or GlobalId: ' + item);
        if (!objectIndex) {
          throw new Error('cannot resolve GlobalId "' + item +
                          '" — await viewer.getObjects() first (it loads the element table)');
        }
        const id = objectIndex.get(item);
        if (id === undefined) throw new Error('unknown GlobalId: ' + item);
        return id;
      });
    }

    // Byte-source registry the wasm reads lazily: a picked File (Blob.slice) or
    // a remote URL (HTTP Range). load_ifcview_from_source_c(sid) streams one.
    Module.__ifcvSources = Module.__ifcvSources || [];

    // The wasm calls this on every single-object pick; (0, '', -1, -1) means the
    // selection was cleared. modelIndex is the picked object's model in load
    // order (matches the modelProgress index) and sourceId the source it was
    // added from, either null when unknown. A marquee box-select does NOT fire
    // this (it has no single object) — use onSelectionChange for that.
    Module.__ifcvOnSelect = function (objectId, guid, modelIndex, sourceId) {
      const detail = {
        objectId: objectId >>> 0,
        guid: guid || null,
        modelIndex: (typeof modelIndex === 'number' && modelIndex >= 0) ? modelIndex : null,
        sourceId: (typeof sourceId === 'number' && sourceId >= 0) ? sourceId : null,
      };
      selectListeners.forEach(function (cb) {
        try { cb(detail); } catch (e) { console.error(e); }
      });
      try {
        document.dispatchEvent(new CustomEvent('ifcviewer:select', { detail: detail }));
      } catch (_) { /* older browsers */ }
    };

    // The wasm pings this whenever it mutates the selection (pick, marquee,
    // hide-selected); the programmatic setters below call it too. It carries no
    // payload — listeners pull the current id set back through getSelection(),
    // so there is exactly one source of truth.
    Module.__ifcvOnSelectionChange = function () {
      const ids = api.getSelection();
      selectionListeners.forEach(function (cb) {
        try { cb(ids); } catch (e) { console.error(e); }
      });
      try {
        document.dispatchEvent(new CustomEvent('ifcviewer:selectionchange', { detail: ids }));
      } catch (_) { /* older browsers */ }
    };

    // The wasm calls this once a model is fully in the scene, with the source
    // id it was loaded from and the session model id the core assigned it. By
    // the time it fires the federation layer has already applied any staged
    // transform and (for the first model) the false-origin guess, so a handler
    // sees the model where it will actually sit rather than mid-placement.
    Module.__ifcvOnModelLoaded = function (sourceId, sessionModelId) {
      const detail = { sourceId: sourceId | 0, sessionModelId: sessionModelId >>> 0 };
      modelLoadedListeners.forEach(function (cb) {
        try { cb(detail); } catch (e) { console.error(e); }
      });
      try {
        document.dispatchEvent(new CustomEvent('ifcviewer:modelloaded', { detail: detail }));
      } catch (_) { /* older browsers */ }
    };

    // Completion side of ifcv_request_objects_c: the element tables have all
    // landed and the scene's objects are ready as JSON. `token` matches the
    // request to its pending Promise.
    // token -> {rows, resolve}. The wasm side streams the objects array one
    // model per batch (so the whole-scene JSON never exists in one string on
    // its heap); Done resolves with the accumulated rows.
    const pendingObjects = new Map();
    let objectsToken = 0;
    Module.__ifcvOnObjectsBatch = function (token, json) {
      const pending = pendingObjects.get(token);
      if (!pending) return;
      const rows = JSON.parse(json);
      for (let i = 0; i < rows.length; ++i) pending.rows.push(rows[i]);
    };
    Module.__ifcvOnObjectsDone = function (token) {
      const pending = pendingObjects.get(token);
      if (!pending) return;
      pendingObjects.delete(token);
      pending.resolve(pending.rows);
    };

    // Some test harnesses / the fullscreen page want the raw module on window.
    if (opts.exposeAsModuleGlobal) global.Module = Module;

    function registerFile(file) {
      const sid = Module.__ifcvSources.length;
      Module.__ifcvSources.push({ file: file, url: null, size: file.size });
      return sid;
    }
    async function registerUrl(url) {
      const size = await sizeUrl(url);
      if (!size) throw new Error('could not size ' + url + ' (need HEAD or Range support)');
      const sid = Module.__ifcvSources.length;
      Module.__ifcvSources.push({ file: null, url: url, size: size });
      return sid;
    }

    api = {
      module: Module,
      ready: ready,
      sidecarFormatVersion: sidecarFormatVersion,
      isLive: function () { return live; },

      // ---- Events ----------------------------------------------------------

      // Single-object picks (click). Fires with
      // {objectId, guid, modelIndex, sourceId}. Returns an unsubscribe function.
      onSelect: function (cb) {
        selectListeners.push(cb);
        return function () {
          const i = selectListeners.indexOf(cb);
          if (i >= 0) selectListeners.splice(i, 1);
        };
      },

      // Any selection change — click, box-select, or a programmatic setter.
      // Fires with the full array of selected objectIds.
      onSelectionChange: function (cb) {
        selectionListeners.push(cb);
        return function () {
          const i = selectionListeners.indexOf(cb);
          if (i >= 0) selectionListeners.splice(i, 1);
        };
      },

      // ---- Camera ----------------------------------------------------------

      // The orbit camera's full state. `eye` is derived from the other four by
      // the wasm (it owns the orbit convention) and is read-only — to move the
      // camera, set target/distance/yaw/pitch.
      getCamera: function () {
        const ptr = Module._malloc(9 * 4);
        try {
          Module._ifcv_get_camera_c(ptr);
          const f = Module.HEAPF32.subarray(ptr >>> 2, (ptr >>> 2) + 9);
          return {
            target:   [f[0], f[1], f[2]],
            distance: f[3],
            yaw:      f[4],   // degrees, about world +Z
            pitch:    f[5],   // degrees above the XY plane, clamped to ±89.9
            eye:      [f[6], f[7], f[8]],
            ortho:    Module._projection_is_ortho_c() !== 0,
          };
        } finally {
          Module._free(ptr);
        }
      },

      // Set any subset of the camera state; omitted fields keep their current
      // value, so `setCamera({ yaw: 90 })` is a pure turn.
      setCamera: function (c) {
        c = c || {};
        const cur = this.getCamera();
        const t = c.target || cur.target;
        Module._ifcv_set_camera_c(
          t[0], t[1], t[2],
          c.distance !== undefined ? c.distance : cur.distance,
          c.yaw      !== undefined ? c.yaw      : cur.yaw,
          c.pitch    !== undefined ? c.pitch    : cur.pitch);
        if (c.ortho !== undefined) Module._ifcv_set_ortho_c(c.ortho ? 1 : 0);
      },

      // ---- Background ------------------------------------------------------

      // Clear colour, as '#rgb' / '#rrggbb' / '#rrggbbaa' or {r, g, b, a} with
      // 0-255 channels. Alpha defaults to opaque.
      //
      // Unlike setColor, an alpha of 0 here is meaningful rather than the "no
      // override" sentinel: it clears the canvas to nothing, letting whatever
      // is behind it in the DOM show through. Stack anything under the canvas
      // — another 3D view, a map, ordinary page content — and the model draws
      // on top of it. There is no depth interaction: the layer behind is
      // strictly behind, so it reads as a backdrop and cannot occlude the
      // model. Requires a platform that composites the canvas with alpha;
      // where it does not, the colour still applies and the alpha is ignored.
      setBackground: function (color) {
        let r, g, b, a = 255;
        if (typeof color === 'string') {
          let hex = color.replace(/^#/, '');
          if (hex.length === 3) hex = hex.split('').map(function (c) { return c + c; }).join('');
          if (hex.length !== 6 && hex.length !== 8) {
            throw new Error('setBackground: expected #rgb, #rrggbb or #rrggbbaa, got ' + color);
          }
          r = parseInt(hex.slice(0, 2), 16);
          g = parseInt(hex.slice(2, 4), 16);
          b = parseInt(hex.slice(4, 6), 16);
          if (hex.length === 8) a = parseInt(hex.slice(6, 8), 16);
        } else if (color && typeof color === 'object') {
          r = color.r | 0; g = color.g | 0; b = color.b | 0;
          if (color.a !== undefined) a = color.a | 0;
        } else {
          throw new Error('setBackground: expected a colour, got ' + color);
        }
        Module._ifcv_set_background_c(r / 255, g / 255, b / 255, a / 255);
      },

      // ---- Navigation ------------------------------------------------------

      // Which mouse buttons orbit / pan / select, as one of NAV_PRESETS:
      //   blender  MMB orbit · Shift+MMB pan · LMB select
      //   rhino    RMB orbit · Shift+RMB pan · LMB select
      //   revit    Shift+MMB orbit · MMB pan · LMB select
      //   web      LMB orbit · MMB pan · RMB select   (the default)
      // The wheel zooms under all four. Also settable up-front as the
      // `navPreset` option to create().
      setNavPreset: function (name) {
        if (NAV_PRESETS.indexOf(name) < 0) {
          throw new Error('unknown nav preset: ' + name +
                          ' (expected one of ' + NAV_PRESETS.join(', ') + ')');
        }
        Module.ccall('ifcv_set_nav_preset_c', null, ['string'], [name]);
      },

      // id: 0 Front, 1 Back, 2 Left, 3 Right, 4 Top, 5 Bottom.
      setStandardView: function (id) { Module._standard_view_c(id | 0); },
      viewAll:        function () { Module._view_all_c(); },
      frameSelection: function () { Module._frame_selection_c(); },

      // ---- Selection -------------------------------------------------------

      // The selected objectIds, ascending.
      getSelection: function () {
        return readIdArray(function (ptr, max) {
          return Module._ifcv_get_selection_c(ptr, max);
        });
      },
      // The last single-clicked object — what a properties panel should show.
      // 0 when nothing is selected.
      getActiveObject: function () { return Module._ifcv_get_active_object_c() >>> 0; },

      // Selected objects with their IFC identity attached. Requires the element
      // table (getObjects()); falls back to bare ids before then.
      getSelectedObjects: function () {
        return api.getSelection().map(function (id) {
          return (objectsById && objectsById.get(id)) || { objectId: id };
        });
      },

      // Each takes an objectId, a GlobalId, an element from getObjects(), or an
      // array of any of those. setSelection replaces (empty/null clears).
      setSelection:        function (x) { applySelection(x, 0); },
      addToSelection:      function (x) { applySelection(x, 1); },
      removeFromSelection: function (x) { applySelection(x, 2); },
      clearSelection:      function ()  { applySelection([], 0); },

      // ---- Objects ---------------------------------------------------------

      // Every object in the scene:
      // [{objectId, guid, name, type, model, sourceId}], where `model` is the
      // index into the load-ordered model list (same index as modelProgress)
      // and `sourceId` the source the model was added from — see the model
      // identity note at the top of the file. Asynchronous — the element tables
      // are fetched lazily per model so first paint never waits on them.
      // Resolving this is also what lets every other call accept GlobalIds; the
      // result is cached for that.
      getObjects: function () {
        const token = ++objectsToken;
        return new Promise(function (resolve) {
          pendingObjects.set(token, { rows: [], resolve: resolve });
          Module._ifcv_request_objects_c(token);
        }).then(function (objects) {
          objectIndex = new Map();
          objectsById = new Map();
          objects.forEach(function (o) {
            if (o.guid) objectIndex.set(o.guid, o.objectId);
            objectsById.set(o.objectId, o);
          });
          return objects;
        });
      },

      // ---- Visibility ------------------------------------------------------

      hide:    function (x) { this.setVisible(x, false); },
      show:    function (x) { this.setVisible(x, true); },
      showAll: function () { Module._show_all_c(); },
      hideAll: function () { Module._hide_all_c(); },
      setVisible: function (x, visible) {
        withIdArray(resolveIds(x), function (ptr, n) {
          Module._ifcv_set_visible_c(ptr, n, visible ? 1 : 0);
        });
      },
      // The hidden objectIds, ascending.
      getHidden: function () {
        return readIdArray(function (ptr, max) {
          return Module._ifcv_get_hidden_c(ptr, max);
        });
      },
      // Selection-driven visibility, matching the H / Shift+H / Alt+H hotkeys.
      hideSelected:    function () { Module._hide_selected_c(); },
      isolateSelected: function () { Module._isolate_selected_c(); },

      // The white-on-dark halo drawn around selected objects (on by default).
      // The renderer also tints the selection blue, which says nothing when
      // the object is already blue — hence a cue that does not depend on the
      // object's colour. Turn it off to get the tint alone.
      setSelectionOutline: function (on) {
        Module._ifcv_set_selection_outline_c(on ? 1 : 0);
      },
      selectionOutlineEnabled: function () {
        return Module._ifcv_selection_outline_is_on_c() !== 0;
      },

      // ---- Colour ----------------------------------------------------------

      // Paint objects a flat colour, replacing whatever the model baked in.
      // `color` is '#rrggbb' / '#rrggbbaa' / {r,g,b,a}, or null to restore the
      // model's own colour. An alpha below 255 makes the object translucent —
      // it moves to the transparent pass on the next frame.
      setColor: function (x, color) {
        const rgba = packColor(color);
        withIdArray(resolveIds(x), function (ptr, n) {
          Module._ifcv_set_color_c(ptr, n, rgba);
        });
      },
      // Drop every override in the scene at once.
      clearColors: function () { Module._ifcv_clear_colors_c(); },

      // ---- Scene -----------------------------------------------------------

      // Drops every model. The element table goes with them, so GlobalIds stop
      // resolving until the next getObjects().
      clearScene: function () {
        objectIndex = null;
        objectsById = null;
        if (Module._clear_scene_c) Module._clear_scene_c();
      },
      toggleXray:   function () { Module._toggle_xray_c(); },
      xrayActive:   function () { return Module._xray_is_active_c() !== 0; },

      // Sparse RGB line grids. A default "base" grid is created with the GPU
      // app. upsertGrid replaces a grid with the same id.
      //   viewer.upsertGrid({ id: 'floor', plane: 'xy', origin: [0, 0, 0],
      //                       spacing: 5, divisions: 20, opacity: 0.55 });
      setGridVisible: function (visible) {
        if (Module._set_grid_visible_c) Module._set_grid_visible_c(visible ? 1 : 0);
      },
      gridVisible: function () {
        return Module._grid_is_visible_c ? Module._grid_is_visible_c() !== 0 : true;
      },
      toggleGrid: function () {
        if (Module._toggle_grid_c) Module._toggle_grid_c();
      },

      // Blender floor axes through the scene origin. `size` is metres either
      // side along X (red) and Y (green). There is no Z line. They fade into
      // the background with the grid. A number is that size; an object may
      // also set `visible`. Default size is 1000.
      //   viewer.setOriginAxes(1000);
      //   viewer.setOriginAxes({ size: 2500, visible: true });
      setOriginAxes: function (opts) {
        if (typeof opts === 'number') opts = { size: opts };
        opts = opts || {};
        if (opts.size != null && Module._set_origin_axes_size_c) {
          Module._set_origin_axes_size_c(Number(opts.size));
        }
        if (opts.visible != null) this.setOriginAxesVisible(!!opts.visible);
        return { size: this.originAxesSize(), visible: this.originAxesVisible() };
      },
      originAxesSize: function () {
        return Module._origin_axes_size_c ? Module._origin_axes_size_c() : 1000;
      },
      setOriginAxesVisible: function (visible) {
        if (Module._set_origin_axes_visible_c) Module._set_origin_axes_visible_c(visible ? 1 : 0);
      },
      originAxesVisible: function () {
        return Module._origin_axes_visible_c ? Module._origin_axes_visible_c() !== 0 : false;
      },
      toggleOriginAxes: function () {
        if (Module._toggle_origin_axes_c) Module._toggle_origin_axes_c();
      },

      // Floor fade for the grid and the X/Y axes. `near` and `far` are
      // multiples of the camera distance: 0.35 starts the fade at 35% of
      // the view distance, 2.2 finishes it at 2.2× that distance. `mode` is
      // 'linear' or 'exp2'. The colour is the background. Off leaves the
      // floor at full strength out to the grid edge.
      //   viewer.setFog({ near: 0.35, far: 2.2 });
      //   viewer.setFog(false);
      setFog: function (opts) {
        if (typeof opts === 'boolean') opts = { enabled: opts };
        opts = opts || {};
        const cur = this.fog();
        const enabled = opts.enabled != null ? !!opts.enabled : cur.enabled;
        let mode = cur.mode;
        if (opts.mode === 'exp2' || opts.mode === 2) mode = 2;
        else if (opts.mode === 'linear' || opts.mode === 1) mode = 1;
        const near = opts.near != null ? Number(opts.near) : cur.near;
        const far = opts.far != null ? Number(opts.far) : cur.far;
        const density = opts.density != null ? Number(opts.density) : cur.density;
        if (Module._set_fog_c) Module._set_fog_c(enabled ? 1 : 0, mode, near, far, density);
        return this.fog();
      },
      fog: function () {
        const fallback = { enabled: true, mode: 1, near: 0.35, far: 2.2, density: 0.002 };
        if (!Module._get_fog_c) return fallback;
        const ptr = Module._malloc(5 * 4);
        try {
          Module._get_fog_c(ptr);
          const d = Module.HEAPF32.subarray(ptr >>> 2, (ptr >>> 2) + 5);
          return {
            enabled: d[0] !== 0,
            mode: d[1] >= 1.5 ? 2 : 1,
            near: d[2],
            far: d[3],
            density: d[4],
          };
        } finally {
          Module._free(ptr);
        }
      },
      setFogVisible: function (visible) {
        if (Module._set_fog_enabled_c) Module._set_fog_enabled_c(visible ? 1 : 0);
      },
      fogVisible: function () {
        return Module._fog_is_enabled_c ? Module._fog_is_enabled_c() !== 0 : true;
      },
      toggleFog: function () {
        if (Module._toggle_fog_c) Module._toggle_fog_c();
      },

      // CSS pixels of a world point on the canvas, y down from the canvas
      // top-left. Null when the point is behind the camera. World (0,0,0) is
      // where the false origin (the survey marker) is drawn. The axes cross
      // at worldOrigin(). Uses the renderer's
      // own projection when this build exports it, and the same orbit math
      // otherwise.
      projectWorld: function (xyz) {
        xyz = xyz || [0, 0, 0];
        if (projectWorldNative !== false && typeof Module._ifcv_project_world_c === 'function') {
          const ptr = Module._malloc(2 * 4);
          try {
            const ok = Module._ifcv_project_world_c(xyz[0], xyz[1], xyz[2], ptr);
            projectWorldNative = true;
            if (!ok) return null;
            const f = Module.HEAPF32.subarray(ptr >>> 2, (ptr >>> 2) + 2);
            return { x: f[0], y: f[1] };
          } catch (err) {
            projectWorldNative = false;
          } finally {
            Module._free(ptr);
          }
        }
        return projectWorldFromCamera(this.getCamera(), opts.canvas, xyz);
      },

      // Pin `el` on the survey marker (the false origin, viewer 0, 0, 0). It
      // stays hidden until the marker is clicked; another click on it, or a
      // click anywhere else on the canvas, hides it again. The text is the
      // false origin in the federation unit, grid north, and whether it was
      // guessed or set. When the point moves, the line leads with how far.
      // Hidden while the axes themselves are hidden. Returns an unbind fn.
      bindOriginReadout: function (el) {
        if (!el) return function () {};
        const viewerApi = this;
        const canvas = opts.canvas;
        const HIT_PX = 18;
        const CLICK_SLOP_PX = 4;
        let open = false;
        let down = null;
        let prev = null;
        let movedUntil = 0;
        let movedNote = '';
        const onDown = function (ev) {
          down = ev.button === 0 ? { x: ev.clientX, y: ev.clientY } : null;
        };
        const onUp = function (ev) {
          if (!down || ev.button !== 0) return;
          const dragged = Math.hypot(ev.clientX - down.x, ev.clientY - down.y) > CLICK_SLOP_PX;
          down = null;
          if (dragged || !viewerApi.originAxesVisible()) return;
          const screen = viewerApi.projectWorld([0, 0, 0]);
          const rect = canvas.getBoundingClientRect();
          const hit = !!screen && Math.hypot(ev.clientX - rect.left - screen.x,
                                             ev.clientY - rect.top - screen.y) <= HIT_PX;
          open = hit ? !open : false;
          if (!open) el.hidden = true;
        };
        canvas.addEventListener('pointerdown', onDown);
        canvas.addEventListener('pointerup', onUp);
        el.hidden = true;
        const tickReadout = function (viewer) {
          if (!viewer.originAxesVisible()) {
            el.hidden = true;
            return;
          }
          const origin = viewer.getFalseOrigin();
          const unit = origin.unit || 'm';
          const now = performance.now();
          if (prev && originMoved(prev, origin)) {
            const dx = origin.xyz[0] - prev.xyz[0];
            const dy = origin.xyz[1] - prev.xyz[1];
            const dz = origin.xyz[2] - prev.xyz[2];
            movedNote = 'moved ' + fmtCoord(Math.hypot(dx, dy, dz)) + ' ' + unit;
            movedUntil = now + 6000;
          }
          prev = { xyz: origin.xyz.slice(), rzDeg: origin.rzDeg, explicit: origin.explicit };
          if (!open) {
            el.hidden = true;
            return;
          }
          const moving = now < movedUntil;
          const xyz = fmtCoord(origin.xyz[0]) + ', ' +
            fmtCoord(origin.xyz[1]) + ', ' +
            fmtCoord(origin.xyz[2]) + ' ' + unit;
          const how = origin.explicit ? 'set' :
            (originShifted(origin.xyz) || Math.abs(origin.rzDeg) > 1e-3 ? 'guessed' : 'none yet');
          const rect = canvas.getBoundingClientRect();
          const screen = viewer.projectWorld([0, 0, 0]);
          const onScreen = screen &&
            screen.x >= 8 && screen.y >= 8 &&
            screen.x <= rect.width - 8 && screen.y <= rect.height - 8;
          el.textContent = 'false origin ' + xyz + '\n' +
            'grid north ' + origin.rzDeg.toFixed(2) + '° · ' + how +
            (moving ? ' · ' + movedNote : '') +
            (onScreen ? '' : ' · off screen');
          el.classList.toggle('moved', moving);
          el.classList.toggle('docked', !onScreen);
          el.hidden = false;
          if (onScreen) {
            const right = screen.x + 22 + el.offsetWidth <= rect.width;
            el.style.left = (rect.left + (right ? screen.x + 12
                                                : screen.x - 32 - el.offsetWidth)) + 'px';
            el.style.top = (rect.top + screen.y) + 'px';
          } else {
            el.style.left = (rect.left + 12) + 'px';
            el.style.top = (rect.top + 36) + 'px';
          }
        };
        frameListeners.push(tickReadout);
        return function () {
          const i = frameListeners.indexOf(tickReadout);
          if (i >= 0) frameListeners.splice(i, 1);
          canvas.removeEventListener('pointerdown', onDown);
          canvas.removeEventListener('pointerup', onUp);
          el.hidden = true;
        };
      },
      // `origin` is in world metres, like the floor axes and the models, so a
      // grid stays put when the false origin changes.
      upsertGrid: function (definition) {
        var grid = normalizeGridDefinition(definition || {});
        if (!grid.id) throw new Error('Grid definition requires an id.');
        gridRegistry[grid.id] = grid;
        upsertGridWasm(Module, grid);
        return Object.assign({}, grid);
      },
      removeGrid: function (id) {
        if (!id || !gridRegistry[id]) return false;
        delete gridRegistry[id];
        removeGridWasm(Module, id);
        if (Module._viewer_request_frame) Module._viewer_request_frame();
        return true;
      },
      clearGrids: function () {
        gridRegistry = Object.create(null);
        if (Module._grid_clear_c) Module._grid_clear_c();
        if (Module._viewer_request_frame) Module._viewer_request_frame();
      },
      listGrids: function () {
        return Object.keys(gridRegistry).map(function (id) {
          return Object.assign({}, gridRegistry[id]);
        });
      },
      applyGrids: function (definitions) {
        gridRegistry = Object.create(null);
        if (Module._grid_clear_c) Module._grid_clear_c();
        var applied = [];
        for (var i = 0; i < (definitions || []).length; i++) {
          var grid = normalizeGridDefinition(definitions[i] || {});
          if (!grid.id) continue;
          gridRegistry[grid.id] = grid;
          upsertGridWasm(Module, grid);
          applied.push(Object.assign({}, grid));
        }
        if (Module._viewer_request_frame) Module._viewer_request_frame();
        return applied;
      },

      // Model bookkeeping (ordered by load). Progress is per-model chunk counts.
      modelCount: function () { return Module._ifcv_model_count_c ? Module._ifcv_model_count_c() : 0; },
      modelProgress: function (i) {
        return {
          resident: Module._ifcv_model_resident_c ? Module._ifcv_model_resident_c(i) : 0,
          total:    Module._ifcv_model_total_c    ? Module._ifcv_model_total_c(i)    : 0,
        };
      },
      bytes: function () {
        return {
          total:  Module._ifcv_bytes_total_c  ? Module._ifcv_bytes_total_c()  : 0,
          needed: Module._ifcv_bytes_needed_c ? Module._ifcv_bytes_needed_c() : 0,
          loaded: Module._ifcv_bytes_loaded_c ? Module._ifcv_bytes_loaded_c() : 0,
        };
      },

      // The latest frame's statistics — what BonsaiViewer's status bar shows.
      // `vram` is the streamed-geometry cache: bytes held by resident chunks,
      // the pool's current capacity, and the budget it may grow to (0 while
      // unbounded). `workingSet` is what the camera wants resident: chunks in
      // view and large enough to draw, how many of those are not resident,
      // and their size — transiently non-zero after a camera move, and
      // persistently non-zero when the scene does not fit in GPU memory
      // (unload a model to make room). Null before the first frame.
      stats: function () {
        const n = 13;
        const ptr = Module._malloc(n * 8);
        try {
          if (!Module._ifcv_get_frame_stats_c(ptr, n)) return null;
          const d = Module.HEAPF64.subarray(ptr >>> 3, (ptr >>> 3) + n);
          return {
            fps: d[0],
            frameTimeMs: d[1],
            objects:   { visible: d[3], total: d[2] },
            triangles: { visible: d[5], total: d[4] },
            drawCalls: d[6],
            vram: { usedBytes: d[7], capacityBytes: d[8], budgetBytes: d[9] },
            workingSet: { chunks: d[10], chunksMissing: d[11], missingBytes: d[12] },
          };
        } finally {
          Module._free(ptr);
        }
      },

      // GPU residency per model, by source id. Unloading frees everything
      // the model holds on the GPU while it stays in the scene (its
      // visibility untouched); loading brings it back, streaming the
      // geometry in again on demand. loadModel resolves false when the
      // device cannot fit the model's buffers. This is the lever when
      // stats().workingSet.chunksMissing stays above zero.
      unloadModel:    function (sourceId) { Module._ifcv_unload_model_c(sourceId | 0); },
      loadModel:      function (sourceId) { return Module._ifcv_load_model_c(sourceId | 0) !== 0; },
      modelUnloaded:  function (sourceId) { return Module._ifcv_model_unloaded_c(sourceId | 0) !== 0; },
      modelVramBytes: function (sourceId) { return Module._ifcv_model_vram_bytes_c(sourceId | 0); },

      registerFileSource: registerFile,
      registerUrlSource: registerUrl,

      // Add a model to the scene. `replace: true` drops the current scene first;
      // otherwise it appends (a lightweight federation of streamed models).
      // Returns the source id: the federation handle for this model. It is
      // valid immediately, before the model has streamed, so a transform or
      // name can be set against it right away — see setModelTransform.
      addFile: async function (file, o) {
        assertSidecarHead(await readSidecarHead(file), sidecarFormatVersion);
        if (o && o.replace) this.clearScene();
        const sid = registerFile(file);
        if (o && o.name) this.setModelName(sid, o.name);
        Module._load_ifcview_from_source_c(sid);
        return sid;
      },
      // `cache: true` keeps a local OPFS copy filled from the viewer's own
      // ranged reads (see the OPFS model cache section above): the next visit
      // loads it with zero geometry traffic, and a complete copy still opens
      // when the server is unreachable. Falls back to plain URL streaming
      // wherever the cache cannot help (no OPFS, no validators from the
      // server, another tab already filling this entry).
      addUrl: async function (url, o) {
        if (o && o.replace) this.clearScene();
        // The header says which sidecar format the file actually is. A
        // network failure is not a format error: with cache enabled, a
        // complete local copy of this same format can still open offline.
        let offline = null;
        try {
          assertSidecarHead(await readSidecarHead(url), sidecarFormatVersion);
        } catch (err) {
          if (err && err.sidecarFormat) throw err;
          if (!(o && o.cache)) throw err;
          offline = err;
        }
        let sid = null;
        if (o && o.cache) {
          const cached = await cachedUrlSource(url, sidecarFormatVersion).catch(() => null);
          if (cached) {
            const src = cached.file || cached.source;
            sid = Module.__ifcvSources.length;
            Module.__ifcvSources.push({ file: src, url: null, size: src.size });
          }
        }
        if (sid === null) {
          if (offline) throw offline;
          sid = await registerUrl(url);
        }
        if (o && o.name) this.setModelName(sid, o.name);
        Module._load_ifcview_from_source_c(sid);
        return sid;
      },
      // Append the small sample baked into the wasm (a slab, a wall and a
      // beam). It is read from memory, not a source, so there is no source id
      // to return. Returns false if this build has no sample to load.
      loadSample: function () {
        if (!Module._load_sample_c) return false;
        objectIndex = null;
        objectsById = null;
        return Module._load_sample_c() !== 0;
      },

      // What the OPFS cache holds: [{url, size, cachedBytes, complete}] plus
      // the browser's storage estimate. Entries whose ledger has not caught
      // up with the last few reads under-report slightly; nothing over-reports.
      cacheInfo: async function () {
        const out = { entries: [], estimate: null };
        try {
          const dir = await cacheDirHandle(false);
          for await (const key of dir.keys()) {
            if (!key.endsWith('.meta')) continue;
            try {
              const meta = JSON.parse(await (await
                (await dir.getFileHandle(key)).getFile()).text());
              if (meta.formatVersion !== sidecarFormatVersion) continue;
              out.entries.push({
                url: meta.url,
                formatVersion: meta.formatVersion,
                size: meta.size,
                cachedBytes: spansBytes(meta.spans),
                complete: spansCover(meta.spans, 0, meta.size),
              });
            } catch (err) { /* torn meta: skip */ }
          }
        } catch (err) { /* no cache dir yet */ }
        if (navigator.storage && navigator.storage.estimate) {
          out.estimate = await navigator.storage.estimate().catch(() => null);
        }
        return out;
      },

      // Drop cached models — one URL, or everything. Sources already handed
      // to the viewer keep working (open handles and Files stay readable);
      // the next visit simply streams from the network again.
      clearCache: async function (url) {
        try {
          const dir = await cacheDirHandle(false);
          const only = url ? await cacheEntryName(url, sidecarFormatVersion) : null;
          const names = [];
          for await (const key of dir.keys()) {
            const base = key.endsWith('.meta') ? key.slice(0, -5) : key;
            if (!only || base === only) names.push(key);
          }
          let n = 0;
          for (const key of names) {
            await dir.removeEntry(key).catch(() => {});
            if (!key.endsWith('.meta')) n++;
          }
          return n;
        } catch (err) {
          return 0;
        }
      },

      // ---- Federation ------------------------------------------------------
      //
      // The concepts an .ifcfed file carries, without the file format: a
      // federation unit, a false origin, and a per-model transform. Parse
      // .ifcfed (or any manifest) in your own code and drive these.
      //
      // Models resolve to global coordinates by default: each one's
      // IfcCoordinateOperation is baked into its .ifcview and applied on load,
      // so models with different map conversions line up. The first model also
      // sets a false origin automatically, which keeps the scene near the
      // origin — necessary because per-instance transforms are float32 and
      // surveyor coordinates would otherwise quantise to ~0.5 m. Call
      // setFalseOrigin yourself to override; that suppresses the guess.

      onModelLoaded: function (cb) {
        modelLoadedListeners.push(cb);
        return function () {
          const i = modelLoadedListeners.indexOf(cb);
          if (i >= 0) modelLoadedListeners.splice(i, 1);
        };
      },

      // Federation unit: an IfcSIUnit name with optional SI prefix
      // ({name:'METRE', prefix:'MILLI'}) or a conversion-based unit
      // ({name:'foot'}). This is the value space for the false origin and for
      // a transform's b/pivot.
      setFederationUnit: function (u) {
        u = u || {};
        federationUnit = { name: u.name || 'METRE', prefix: u.prefix || '' };
        Module.ccall('ifcv_set_federation_unit_c', null, ['string', 'string'],
                     [federationUnit.name, federationUnit.prefix]);
      },

      // Nominate the survey point, with an optional grid-north heading in
      // degrees, in world coordinates. The models, grids and axes stay where
      // they are; the survey marker moves to this point. Setting this turns
      // off the automatic guess.
      setFalseOrigin: function (o) {
        o = o || {};
        const xyz = o.xyz || [0, 0, 0];
        Module._ifcv_set_false_origin_c(xyz[0], xyz[1], xyz[2], o.rzDeg || 0);
      },

      // The active origin, including one the automatic guess produced.
      // `explicit` is true when it was set rather than guessed.
      getFalseOrigin: function () {
        const ptr = Module._malloc(5 * 8);
        try {
          Module._ifcv_get_false_origin_c(ptr);
          const d = Module.HEAPF64.subarray(ptr >>> 3, (ptr >>> 3) + 5);
          return {
            xyz: [d[0], d[1], d[2]],
            rzDeg: d[3],
            explicit: d[4] !== 0,
            unit: federationUnitLabel(federationUnit),
          };
        } finally {
          Module._free(ptr);
        }
      },

      // Survey point in viewer metres: where the survey marker is drawn.
      // Always (0, 0, 0); the false origin is what the scene is drawn
      // around.
      surveyPoint: function () {
        return [0, 0, 0];
      },

      // World 0, 0, 0 in viewer metres: where the red and green axes cross.
      // The same point as surveyPoint() until a false origin is set.
      worldOrigin: function () {
        return worldOriginInViewer(this.getFalseOrigin(), federationUnit);
      },

      // Place a model: rotate it about `pivot`, then translate so that point
      // `a` lands on point `b`.
      //
      // `aFrame` picks the frame `a` is expressed in: 'global' (default) means
      // post-CoordinateOperation, in the model's map unit — i.e. real-world
      // coordinates. 'local' means pre-CoordinateOperation, in the model's own
      // project unit. b, pivot and the origin are in the federation unit;
      // rotation is degrees, intrinsic XYZ.
      //
      // Safe to call before the model has finished streaming; it is applied
      // when the load completes, so the model never visibly jumps.
      setModelTransform: function (sourceId, xf) {
        xf = xf || {};
        const a = xf.a || [0, 0, 0], b = xf.b || [0, 0, 0];
        const r = xf.rotationDeg || [0, 0, 0], p = xf.pivot || [0, 0, 0];
        Module._ifcv_set_model_transform_c(
          sourceId | 0, xf.aFrame === 'local' ? 0 : 1,
          a[0], a[1], a[2], b[0], b[1], b[2],
          r[0], r[1], r[2], p[0], p[1], p[2]);
      },

      clearModelTransform: function (sourceId) {
        Module._ifcv_clear_model_transform_c(sourceId | 0);
      },

      setModelName: function (sourceId, name) {
        Module.ccall('ifcv_set_model_name_c', null, ['number', 'string'],
                     [sourceId | 0, String(name)]);
      },

      // The georeferencing a model actually carries, read back from its
      // .ifcview: {hasCoordinateOperation, matrix (16, column-major, metres),
      // projectLengthToMeters, mapUnitToMeters}. Null until the model has
      // finished loading.
      getModelGeoref: function (sourceId) {
        const ptr = Module._malloc(19 * 8);
        try {
          if (!Module._ifcv_get_model_georef_c(sourceId | 0, ptr)) return null;
          const d = Module.HEAPF64.subarray(ptr >>> 3, (ptr >>> 3) + 19);
          return {
            hasCoordinateOperation: d[0] !== 0,
            matrix: Array.from(d.subarray(1, 17)),
            projectLengthToMeters: d[17],
            mapUnitToMeters: d[18],
          };
        } finally {
          Module._free(ptr);
        }
      },
    };

    // The nav preset is pure button-table state on the wasm side, so it can be
    // set the moment main() has run (which is by the time `factory` resolved) —
    // no need to wait on `ready`. Doing it here means the very first drag uses
    // the host's scheme rather than the "web" default for a frame or two.
    if (opts.navPreset) api.setNavPreset(opts.navPreset);

    return api;
  }

  global.IfcViewer = { create: create, sizeUrl: sizeUrl, packColor: packColor };
})(window);
