
import initModule from './wasm/ifcopenshell_wasm.mjs';
import { createIfcOpenshellModule } from './wasm/ifcopenshell_api.mjs';

export { createIfcOpenshellModule, initModule };
export const wasmUrl = new URL('./wasm/ifcopenshell_wasm.wasm', import.meta.url).href;
export const pluginBaseUrl = import.meta.url;
export const manifest = {
  "schema": {
    "ifc2x3": { wasm: new URL("./wasm/plugins/ifcopenshell.parse.schema.ifc2x3.wasm", import.meta.url).href },
    "ifc4": { wasm: new URL("./wasm/plugins/ifcopenshell.parse.schema.ifc4.wasm", import.meta.url).href },
    "ifc4x3_add2": { wasm: new URL("./wasm/plugins/ifcopenshell.parse.schema.ifc4x3_add2.wasm", import.meta.url).href },
  },
  "kernel": {
    "cgal": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.kernel.cgal.wasm", import.meta.url).href },
    "cgalsimple": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.kernel.cgalsimple.wasm", import.meta.url).href },
    "opencascade": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.kernel.opencascade.wasm", import.meta.url).href },
    "manifold": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.kernel.manifold.wasm", import.meta.url).href },
    "passthrough": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.kernel.passthrough.wasm", import.meta.url).href },
  },
  "tree": {
    "opencascade.brep": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.tree.opencascade.brep.wasm", import.meta.url).href, depends: ["kernel:opencascade"] },
    "opencascade.trianglebvh": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.tree.opencascade.trianglebvh.wasm", import.meta.url).href, depends: ["kernel:opencascade"] },
  },
  "mapping": {
    "ifc2x3": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.mapping.ifc2x3.wasm", import.meta.url).href },
    "ifc4": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.mapping.ifc4.wasm", import.meta.url).href },
    "ifc4x3_add2": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.mapping.ifc4x3_add2.wasm", import.meta.url).href },
  },
  "document": {
    "xml.ifc2x3": { wasm: new URL("./wasm/plugins/ifcopenshell.document.xml.ifc2x3.wasm", import.meta.url).href },
    "json.ifc2x3": { wasm: new URL("./wasm/plugins/ifcopenshell.document.json.ifc2x3.wasm", import.meta.url).href },
    "xml.ifc4": { wasm: new URL("./wasm/plugins/ifcopenshell.document.xml.ifc4.wasm", import.meta.url).href },
    "json.ifc4": { wasm: new URL("./wasm/plugins/ifcopenshell.document.json.ifc4.wasm", import.meta.url).href },
    "xml.ifc4x3_add2": { wasm: new URL("./wasm/plugins/ifcopenshell.document.xml.ifc4x3_add2.wasm", import.meta.url).href },
    "json.ifc4x3_add2": { wasm: new URL("./wasm/plugins/ifcopenshell.document.json.ifc4x3_add2.wasm", import.meta.url).href },
  },
  "geometry_serializer": {
    "ttl": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.ttl.wasm", import.meta.url).href, depends: ["kernel:opencascade"] },
    "obj": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.obj.wasm", import.meta.url).href },
    "glb": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.glb.wasm", import.meta.url).href },
    "stp": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.stp.wasm", import.meta.url).href, depends: ["kernel:opencascade"] },
    "igs": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.igs.wasm", import.meta.url).href, depends: ["kernel:opencascade"] },
    "svg": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.svg.wasm", import.meta.url).href, depends: ["kernel:opencascade"] },
  },
};
