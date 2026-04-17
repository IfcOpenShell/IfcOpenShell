// ifc_worker.js  (MODULE WORKER)
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v0.29.3/full/pyodide.mjs";

let pyodide = null;
let callToolPy = null;
let initPromise = null;

function ok(id, extra = {}, transfer = []) {
    self.postMessage({ id, ok: true, ...extra }, transfer);
}
function fail(id, error) {
    self.postMessage({ id, ok: false, error: String(error?.message || error) });
}

async function ensurePyodide() {
    if (initPromise) return initPromise;

    initPromise = (async () => {
        // Passing indexURL avoids some environments failing to infer it from the module URL. :contentReference[oaicite:3]{index=3}
        pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v0.29.3/full/",
        });

        await pyodide.loadPackage("micropip");
        await pyodide.loadPackage("numpy");
        await pyodide.loadPackage("shapely");
        await pyodide.loadPackage("typing-extensions");
        
        const micropip = pyodide.pyimport("micropip");
        micropip.install("python-dateutil")
        
        const wheelUrl = "https://ifcopenshell.github.io/wasm-wheels/ifcopenshell-0.8.5-cp313-cp313-pyodide_2025_0_wasm32.whl";

        await micropip.install(wheelUrl);

        await micropip.install([
            "./dist/ifcquery-0.8.5-py3-none-any.whl",
            "./dist/ifcedit-0.8.5-py3-none-any.whl",
            "./dist/ifcopenshell_mcp-0.8.5-py3-none-any.whl",
            "./dist/lark-1.3.1-py3-none-any.whl",
            "./dist/isodate-0.7.2-py3-none-any.whl",
        ])
        await pyodide.runPythonAsync(`
from ifcmcp.embedded import call_tool as _call_tool
    `);
        callToolPy = pyodide.globals.get("_call_tool");
    })();

    return initPromise;
}

function callTool(name, args) {
    const pyArgs = pyodide.toPy(args);
    const res = callToolPy(name, pyArgs);
    pyArgs.destroy();
    const resJs = res.toJs({ dict_converter: Object.fromEntries });
    res.destroy();
    return resJs;
}

self.onmessage = async (ev) => {
    const { id, type, payload } = ev.data || {};
    try {
        if (type === "init") {
            await ensurePyodide();
            ok(id, { result: "ok" });
            return;
        }

        await ensurePyodide();

        if (type === "loadIfc") {
            const { filename, bytes } = payload;
            const path = `/tmp/${filename || "model.ifc"}`;
            pyodide.FS.mkdirTree("/tmp");
            pyodide.FS.writeFile(path, new Uint8Array(bytes));
            const result = callTool("ifc_load", { path });
            ok(id, { result });
            return;
        }

        if (type === "exportIfc") {
            const path = "/tmp/export.ifc";
            const result = callTool("ifc_save", { path });
            const data = pyodide.FS.readFile(path);
            ok(id, { result, filename: "export.ifc", bytes: data }, [data.buffer]);
            return;
        }

        if (type === "toolCall") {
            const { name, args } = payload;
            const result = callTool(name, args || {});
            ok(id, { result });
            return;
        }

        throw new Error(`Unknown message type: ${type}`);
    } catch (e) {
        fail(id, e);
    }
};