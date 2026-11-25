// Run both wheel layouts in fresh Pyodide processes, without RTLD_GLOBAL fixes.
// Usage: node verify_wheels.mjs PYODIDE_DIST WHEEL_DIR MODULAR_WHEEL_DIR
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readdir, readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, join, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const script = fileURLToPath(import.meta.url);
const [pyodideDir, wheelDir, modularDir] = process.argv.slice(2);
assert(pyodideDir && wheelDir && modularDir,
    "Usage: node verify_wheels.mjs PYODIDE_DIST WHEEL_DIR MODULAR_WHEEL_DIR");

if (!process.env.IFCOPENSHELL_VERIFY_WHEEL_LAYOUT) {
    for (const layout of ["monolithic", "modular"]) {
        const result = spawnSync(process.execPath, [script, pyodideDir, wheelDir, modularDir], {
            stdio: "inherit",
            env: { ...process.env, IFCOPENSHELL_VERIFY_WHEEL_LAYOUT: layout },
        });
        if (result.error) throw result.error;
        assert.equal(result.status, 0, `${layout} wheel create_shape verification failed`);
    }
} else {
    try {
        const layout = process.env.IFCOPENSHELL_VERIFY_WHEEL_LAYOUT;
        console.log(`Verifying ${layout} wheels`);
        const { loadPyodide } = createRequire(import.meta.url)(join(resolve(pyodideDir), "pyodide.js"));
        const pyodide = await loadPyodide({ indexURL: resolve(pyodideDir) + sep });
        await pyodide.loadPackage(["numpy", "typing-extensions"]);
        const directory = resolve(layout === "modular" ? modularDir : wheelDir);
        const files = await readdir(directory);
        const prefixes = layout === "modular" ? [
            "ifcopenshell-",
            "ifcopenshell_parse_schema_ifc4-",
            "ifcopenshell_geometry_mapping_ifc4-",
            "ifcopenshell_geometry_kernel_manifold-",
        ] : ["ifcopenshell-"];
        for (const prefix of prefixes) {
            const matches = files.filter(name => name.startsWith(prefix) && name.endsWith(".whl"));
            assert.equal(matches.length, 1, `Expected one ${prefix} wheel in ${directory}: ${matches}`);
            // loadPackage and micropip use the same dynamic-library loader. Using
            // local wheel paths here avoids a separate HTTP server and PyPI access.
            await pyodide.loadPackage(join(directory, matches[0]).split(sep).join("/"), {
                errorCallback: message => { throw new Error(message); },
            });
        }
        await pyodide.runPythonAsync(await readFile(join(dirname(script), "verify_create_shape.py"), "utf8"));
        // Install the fallback only after the Manifold pass, like the demo app.
        if (layout === "modular") {
            const matches = files.filter(name => name.startsWith("ifcopenshell_geometry_kernel_opencascade-") && name.endsWith(".whl"));
            assert.equal(matches.length, 1, "The modular build must include the OpenCascade fallback wheel");
            await pyodide.loadPackage(join(directory, matches[0]).split(sep).join("/"), {
                errorCallback: message => { throw new Error(message); },
            });
        }
        await pyodide.runPythonAsync(`
fallback = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), solid, geometry_library="opencascade")
assert fallback.verts and fallback.faces, "OpenCascade fallback returned an empty mesh"
print("OpenCascade fallback plug-in loaded and create_shape passed")
`);
    } catch (error) {
        // Avoid Node printing the entire minified Pyodide source for an
        // uncaught exception, which can exhaust CI's log limit before the cause.
        console.error(String(error));
        process.exitCode = 1;
    }
}
