import config from '../../../config.json';
import hyperid from 'hyperid';

let pyodide = null;
let id = hyperid();

let LoadedIFC = new Map();

export async function init(pdide) {
    pyodide = pdide;

    // Load Python API bindings
    await pyodide.runPythonAsync(`
        from pyodide.http import pyfetch
        response = await pyfetch("${config.wasm.api_py_url}")
        with open("api.py", "wb") as f:
            f.write(await response.bytes())
    `);
}

export async function getPredefinedTypes(schema, entity) {
    const result = await pyodide.runPythonAsync(`
        from api import get_predefined_types_for_entity
        predef_types = get_predefined_types_for_entity("${schema}", "${entity}")
        predef_types
    `);
    return result.toJs({ dict_converter: Object.fromEntries });
}

export async function getAllEntityClasses(schema) {
    const result = await pyodide.runPythonAsync(`
        from api import get_all_entity_classes
        entities = get_all_entity_classes("${schema}")
        entities
    `);
    return result.toJs({ dict_converter: Object.fromEntries });
}

export async function getAllDataTypes(schema) {
    const result = await pyodide.runPythonAsync(`
        from api import get_all_data_types
        data_types = get_all_data_types("${schema}")
        data_types
    `);
    return result.toJs({ dict_converter: Object.fromEntries });
}

export async function getEntityAttributes(schema, entity) {
    const result = await pyodide.runPythonAsync(`
        from api import get_entity_attributes
        attrs = get_entity_attributes("${schema}", "${entity}")
        attrs
    `);
    return result.toJs({ dict_converter: Object.fromEntries });
}

export async function getApplicablePsets(schema, entity, predefinedType = '') {
    const result = await pyodide.runPythonAsync(`
        from api import get_applicable_psets
        psets = get_applicable_psets("${schema}", "${entity}", "${predefinedType}")
        psets
    `);
    return result.toJs({ dict_converter: Object.fromEntries });
}

export async function getMaterialCategories() {
    const result = await pyodide.runPythonAsync(`
        from api import get_material_categories
        materials = get_material_categories()
        materials
    `);
    return result.toJs({ dict_converter: Object.fromEntries });
}

export async function getStandardClassificationSystems() {
    const result = await pyodide.runPythonAsync(`
        from api import get_standard_classification_systems
        systems = get_standard_classification_systems()
        systems
    `);
    return result.toJs({ dict_converter: Object.fromEntries });
}

export async function loadIfc(ifcData) {
    const ifc_id = id();
    const path = `/tmp/${encodeURIComponent(ifc_id)}.ifc`;

    pyodide.FS.writeFile(path, new Uint8Array(ifcData));
    const ifc = await pyodide.runPythonAsync(`
        import ifcopenshell

        ifc = ifcopenshell.open("${path}")
        ifc
    `);

    LoadedIFC.set(ifc_id, ifc);
    return ifc_id;
}

export async function unloadIfc(ifcId) {
    const path = `/tmp/${encodeURIComponent(ifcId)}.ifc`;

    pyodide.FS.unlink(path);
    LoadedIFC.delete(ifcId);
}

export async function auditIfc(ifcId, idsData) {
    const reporter = pyodide.pyimport("ifctester.reporter");
    const api = pyodide.pyimport("api");

    const idsString = new TextDecoder().decode(new Uint8Array(idsData));
    const specs = api.ids_from_xml_string(idsString, true);
    const ifc = LoadedIFC.get(ifcId);

    // Run audit
    specs.validate(ifc);

    // Create report in both HTML and JSON formats
    let jsonReporter = reporter.Json(specs);
    jsonReporter.report();
    const jsonReport = jsonReporter.to_string();

    let htmlReporter = reporter.Html(specs);
    htmlReporter.report();
    const htmlReport = htmlReporter.to_string();

    return {
        json: JSON.parse(jsonReport),
        html: htmlReport
    };
}

// Expose interface
export const API = {
    "getPredefinedTypes": getPredefinedTypes,
    "getAllEntityClasses": getAllEntityClasses,
    "getAllDataTypes": getAllDataTypes,
    "getEntityAttributes": getEntityAttributes,
    "getApplicablePsets": getApplicablePsets,
    "getMaterialCategories": getMaterialCategories,
    "getStandardClassificationSystems": getStandardClassificationSystems,
    "loadIfc": loadIfc,
    "unloadIfc": unloadIfc,
    "auditIfc": auditIfc
};