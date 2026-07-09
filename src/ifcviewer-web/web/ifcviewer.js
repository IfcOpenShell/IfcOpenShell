// ifcviewer.js — a small JavaScript integration layer over the Emscripten
// module (IfcViewerWeb.js). Load this AFTER IfcViewerWeb.js, which defines the
// global `createIfcViewer` factory.
//
//   <script src="IfcViewerWeb.js"></script>
//   <script src="ifcviewer.js"></script>
//   <script>
//     const viewer = await IfcViewer.create({ canvas: myCanvas });
//     await viewer.ready;                       // GPU app is live
//     viewer.onSelect(({ objectId, guid }) => …);
//     await viewer.addFile(file, { replace: true });
//     await viewer.addUrl('/model.ifcview');    // appends (federation)
//   </script>
//
// The canvas element MUST have id="viewer-canvas" — the wasm side hard-codes
// that selector for its WebGPU surface and input handlers.
(function (global) {
  'use strict';

  // Resolve a remote sidecar's total size so the loader can bound its ranged
  // reads: HEAD Content-Length, falling back to a 0-0 Range's Content-Range.
  async function sizeUrl(url) {
    const head = await fetch(url, { method: 'HEAD' });
    const len = head.ok ? parseInt(head.headers.get('Content-Length') || '0', 10) : 0;
    if (len > 0) return len;
    const probe = await fetch(url, { headers: { Range: 'bytes=0-0' } });
    const cr = probe.headers.get('Content-Range'); // "bytes 0-0/12345"
    return cr ? parseInt(cr.split('/')[1] || '0', 10) : 0;
  }

  // Boot a viewer bound to `opts.canvas`. Resolves to the API object once the
  // wasm runtime is initialised; `api.ready` resolves once the GPU app is live.
  async function create(opts) {
    opts = opts || {};
    const factory = opts.moduleFactory || global.createIfcViewer;
    if (typeof factory !== 'function') {
      throw new Error('createIfcViewer not found — load IfcViewerWeb.js first');
    }

    const selectListeners = [];
    let api = null;   // built below; the RAF loop only reads it after that
    let live = false;
    let resolveReady;
    const ready = new Promise(function (r) { resolveReady = r; });

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
          if (opts.onFrame) opts.onFrame(api);
        }
        requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }

    const Module = await factory({
      canvas: opts.canvas,
      // Keep the runtime alive after main() returns so Dawn-web's async
      // adapter/device callbacks land (they set Module._app_ptr).
      noExitRuntime: true,
      print:    opts.print    || function (t) { console.log(t); },
      printErr: opts.printErr || function (t) { console.warn(t); },
      onRuntimeInitialized: function () { startLoop(this); },
    });

    // Byte-source registry the wasm reads lazily: a picked File (Blob.slice) or
    // a remote URL (HTTP Range). load_sidecar_from_source_c(sid) streams one.
    Module.__ifcvSources = Module.__ifcvSources || [];

    // The wasm calls this on every pick; (0, '', -1) means the selection was
    // cleared. modelIndex is the picked object's model in load order (matches
    // the modelProgress index), or -1.
    Module.__ifcvOnSelect = function (objectId, guid, modelIndex) {
      const detail = {
        objectId: objectId >>> 0,
        guid: guid || null,
        modelIndex: (typeof modelIndex === 'number' && modelIndex >= 0) ? modelIndex : null,
      };
      selectListeners.forEach(function (cb) {
        try { cb(detail); } catch (e) { console.error(e); }
      });
      try {
        document.dispatchEvent(new CustomEvent('ifcviewer:select', { detail: detail }));
      } catch (_) { /* older browsers */ }
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
      isLive: function () { return live; },

      // Register a selection listener; returns an unsubscribe function.
      onSelect: function (cb) {
        selectListeners.push(cb);
        return function () {
          const i = selectListeners.indexOf(cb);
          if (i >= 0) selectListeners.splice(i, 1);
        };
      },

      // Scene / camera passthroughs.
      clearScene:     function () { if (Module._clear_scene_c)      Module._clear_scene_c(); },
      viewAll:        function () { if (Module._view_all_c)         Module._view_all_c(); },
      frameSelection: function () { if (Module._frame_selection_c)  Module._frame_selection_c(); },

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

      registerFileSource: registerFile,
      registerUrlSource: registerUrl,

      // Add a model to the scene. `replace: true` drops the current scene first;
      // otherwise it appends (a lightweight federation of streamed models).
      addFile: async function (file, o) {
        if (o && o.replace) this.clearScene();
        Module._load_sidecar_from_source_c(registerFile(file));
      },
      addUrl: async function (url, o) {
        if (o && o.replace) this.clearScene();
        Module._load_sidecar_from_source_c(await registerUrl(url));
      },
    };
    return api;
  }

  global.IfcViewer = { create: create, sizeUrl: sizeUrl };
})(window);
