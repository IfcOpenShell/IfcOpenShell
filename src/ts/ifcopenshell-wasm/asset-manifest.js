
import initModule from './wasm/ifcopenshell_wasm.mjs';
import { createIfcOpenshellModule } from './wasm/ifcopenshell_api.mjs';

export { createIfcOpenshellModule, initModule };
export const wasmUrl = new URL('./wasm/ifcopenshell_wasm.wasm', import.meta.url).href;
export const pluginBaseUrl = import.meta.url;
export const manifest = {
  "schema": {
    "ifc2x3": { wasm: new URL("./wasm/plugins/ifcopenshell_parse_schema_ifc2x3.wasm", import.meta.url).href },
    "ifc4": { wasm: new URL("./wasm/plugins/ifcopenshell_parse_schema_ifc4.wasm", import.meta.url).href },
    "ifc4x3_add2": { wasm: new URL("./wasm/plugins/ifcopenshell_parse_schema_ifc4x3_add2.wasm", import.meta.url).href },
  },
  "kernel": {
    "cgal": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_kernel_cgal.wasm", import.meta.url).href },
    "cgalsimple": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_kernel_cgalsimple.wasm", import.meta.url).href },
    "opencascade": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_kernel_opencascade.wasm", import.meta.url).href },
    "manifold": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_kernel_manifold.wasm", import.meta.url).href },
    "passthrough": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_kernel_passthrough.wasm", import.meta.url).href },
  },
  "tree": {
    "opencascade.brep": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_tree_opencascade_brep.wasm", import.meta.url).href, depends: ["kernel:opencascade"] },
    "opencascade.trianglebvh": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_tree_opencascade_trianglebvh.wasm", import.meta.url).href, depends: ["kernel:opencascade"] },
  },
  "mapping": {
    "ifc2x3": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_mapping_ifc2x3.wasm", import.meta.url).href },
    "ifc4": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_mapping_ifc4.wasm", import.meta.url).href },
    "ifc4x3_add2": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_mapping_ifc4x3_add2.wasm", import.meta.url).href },
  },
  "document": {
    "xml.ifc2x3": { wasm: new URL("./wasm/plugins/ifcopenshell_document_xml_ifc2x3.wasm", import.meta.url).href },
    "json.ifc2x3": { wasm: new URL("./wasm/plugins/ifcopenshell_document_json_ifc2x3.wasm", import.meta.url).href },
    "xml.ifc4": { wasm: new URL("./wasm/plugins/ifcopenshell_document_xml_ifc4.wasm", import.meta.url).href },
    "json.ifc4": { wasm: new URL("./wasm/plugins/ifcopenshell_document_json_ifc4.wasm", import.meta.url).href },
    "xml.ifc4x3_add2": { wasm: new URL("./wasm/plugins/ifcopenshell_document_xml_ifc4x3_add2.wasm", import.meta.url).href },
    "json.ifc4x3_add2": { wasm: new URL("./wasm/plugins/ifcopenshell_document_json_ifc4x3_add2.wasm", import.meta.url).href },
  },
  "geometry_serializer": {
    "ttl": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_ttl.wasm", import.meta.url).href, depends: ["kernel:opencascade"] },
    "obj": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_obj.wasm", import.meta.url).href },
    "glb": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_glb.wasm", import.meta.url).href },
    "stp": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_stp.wasm", import.meta.url).href, depends: ["kernel:opencascade"] },
    "igs": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_igs.wasm", import.meta.url).href, depends: ["kernel:opencascade"] },
    "svg": { wasm: new URL("./wasm/plugins/ifcopenshell_geometry_svg.wasm", import.meta.url).href, depends: ["kernel:opencascade"] },
  },
};
