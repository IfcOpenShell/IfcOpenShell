
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
    "passthrough": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.kernel.passthrough.wasm", import.meta.url).href },
  },
  "mapping": {
    "ifc2x3": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.mapping.ifc2x3.wasm", import.meta.url).href },
    "ifc4": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.mapping.ifc4.wasm", import.meta.url).href },
    "ifc4x3_add2": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.mapping.ifc4x3_add2.wasm", import.meta.url).href },
  },
  "document": {
    "xml.ifc2x3": { wasm: new URL("./wasm/plugins/ifcopenshell.document.xml.ifc2x3.wasm", import.meta.url).href },
    "xml.ifc4": { wasm: new URL("./wasm/plugins/ifcopenshell.document.xml.ifc4.wasm", import.meta.url).href },
    "xml.ifc4x3_add2": { wasm: new URL("./wasm/plugins/ifcopenshell.document.xml.ifc4x3_add2.wasm", import.meta.url).href },
  },
  "geometry_serializer": {
    "ttl": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.ttl.wasm", import.meta.url).href },
    "obj": { wasm: new URL("./wasm/plugins/ifcopenshell.geometry.obj.wasm", import.meta.url).href },
  },
};
