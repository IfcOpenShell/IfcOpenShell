// ifcviewer.js — a small JavaScript integration layer over the Emscripten
// module (IfcViewerWeb.js). Load this AFTER IfcViewerWeb.js, which defines the
// global `createIfcViewer` factory.
//
//   <script src="IfcViewerWeb.js"></script>
//   <script src="ifcviewer.js"></script>
//   <script>
//     const viewer = await IfcViewer.create({ canvas: myCanvas,
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

  // Boot a viewer bound to `opts.canvas`. Resolves to the API object once the
  // wasm runtime is initialised; `api.ready` resolves once the GPU app is live.
  async function create(opts) {
    opts = opts || {};
    const factory = opts.moduleFactory || global.createIfcViewer;
    if (typeof factory !== 'function') {
      throw new Error('createIfcViewer not found — load IfcViewerWeb.js first');
    }

    const selectListeners = [];
    const selectionListeners = [];
    const modelLoadedListeners = [];
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
    // a remote URL (HTTP Range). load_sidecar_from_source_c(sid) streams one.
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
    const pendingObjects = new Map();
    let objectsToken = 0;
    Module.__ifcvOnObjects = function (token, json) {
      const resolve = pendingObjects.get(token);
      if (!resolve) return;
      pendingObjects.delete(token);
      resolve(JSON.parse(json));
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
          pendingObjects.set(token, resolve);
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
      // Returns the source id: the federation handle for this model. It is
      // valid immediately, before the model has streamed, so a transform or
      // name can be set against it right away — see setModelTransform.
      addFile: async function (file, o) {
        if (o && o.replace) this.clearScene();
        const sid = registerFile(file);
        if (o && o.name) this.setModelName(sid, o.name);
        Module._load_sidecar_from_source_c(sid);
        return sid;
      },
      addUrl: async function (url, o) {
        if (o && o.replace) this.clearScene();
        const sid = await registerUrl(url);
        if (o && o.name) this.setModelName(sid, o.name);
        Module._load_sidecar_from_source_c(sid);
        return sid;
      },

      // ---- Federation ------------------------------------------------------
      //
      // The concepts an .ifcfed file carries, without the file format: a
      // federation unit, a false origin, and a per-model transform. Parse
      // .ifcfed (or any manifest) in your own code and drive these.
      //
      // Models resolve to global coordinates by default: each one's
      // IfcCoordinateOperation is baked into its sidecar and applied on load,
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
        Module.ccall('ifcv_set_federation_unit_c', null, ['string', 'string'],
                     [u.name || 'METRE', u.prefix || '']);
      },

      // Nominate a point as the scene origin, with an optional grid-north
      // heading in degrees. Setting this turns off the automatic guess.
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
          return { xyz: [d[0], d[1], d[2]], rzDeg: d[3], explicit: d[4] !== 0 };
        } finally {
          Module._free(ptr);
        }
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
      // sidecar: {hasCoordinateOperation, matrix (16, column-major, metres),
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
