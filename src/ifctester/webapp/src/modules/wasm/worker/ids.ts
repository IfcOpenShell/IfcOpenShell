/**
 * IDS module
 */

let pyodide: any = null;

// IDS Python classes
let Ids: any;
let Specification: any;
let Entity: any;
let Attribute: any;
let Property: any;
let Material: any;
let Classification: any;
let PartOf: any;

export async function init(pdide: any) {
    pyodide = pdide;
    
    await pyodide.loadPackagesFromImports(`
        import ifctester.ids
        import ifctester.facet
    `);

    // Import the core IDS classes
    Ids = pyodide.pyimport("ifctester.ids").Ids;
    Specification = pyodide.pyimport("ifctester.ids").Specification;
    
    // Import facet classes
    Entity = pyodide.pyimport("ifctester.facet").Entity;
    Attribute = pyodide.pyimport("ifctester.facet").Attribute;
    Property = pyodide.pyimport("ifctester.facet").Property;
    Material = pyodide.pyimport("ifctester.facet").Material;
    Classification = pyodide.pyimport("ifctester.facet").Classification;
    PartOf = pyodide.pyimport("ifctester.facet").PartOf;
}

function _idsToInstance(idsObj: Record<string, unknown>) {
    const ids_raw = Ids();
    return ids_raw.parse(pyodide.toPy(idsObj))
}

export function createIDS(): Record<string, unknown> {
    const ids_raw = Ids()
    return ids_raw.asdict().toJs({dict_converter: Object.fromEntries});
}

export function openIDS(ids_xml: string, validate = false): Record<string, unknown> {
    const ids_from_xml_string = pyodide.pyimport("api").ids_from_xml_string;
    const ids_raw = ids_from_xml_string(ids_xml, validate);

    return ids_raw.asdict().toJs({dict_converter: Object.fromEntries});
}

export function validateIDS(idsObj: Record<string, unknown>): boolean {
    const ids_raw = _idsToInstance(idsObj)
    const tempFilename = `temp_${Date.now()}.xml`;
    const isValid = ids_raw.to_xml(tempFilename); // to_xml validates the XML as well, as far as I understand
  
    pyodide.runPython(`
        import os
        if os.path.exists("${tempFilename}"):
            os.remove("${tempFilename}")
    `);
    
    return isValid;
}

export function exportIDS(idsObj: Record<string, unknown>): string {
    const ids_raw = _idsToInstance(idsObj)
    return ids_raw.to_string();
}

export function createSpecification({
    name = "Unnamed",
    ifcVersion = ["IFC2X3", "IFC4"],
    identifier = null,
    description = null,
    instructions = null,
    usage = "required"
}: {
    name?: string;
    ifcVersion?: string[];
    identifier?: string | null;
    description?: string | null;
    instructions?: string | null;
    usage?: string;
} = {}): Record<string, unknown> {
    const spec = Specification.callKwargs({
        name: name,
        ifcVersion: ifcVersion,
        identifier: identifier,
        description: description,
        instructions: instructions
    });
    spec.set_usage(usage);

    return spec.asdict().toJs({dict_converter: Object.fromEntries});
}

// @instructions
export function createEntityFacet(
    clause: string,
    {name = "IFCWALL", predefinedType = null, instructions = null}: {
        name?: string;
        predefinedType?: string | null;
        instructions?: string | null;
    } = {}
): Record<string, unknown> {
    const entity = Entity.callKwargs({
        name: name,
        predefinedType: predefinedType,
        instructions: instructions
    });
    return entity.asdict(clause).toJs({dict_converter: Object.fromEntries});
}

// @cardinality, @instructions
export function createAttributeFacet(
    clause: string,
    {name = "Name", value = null, cardinality = "required", instructions = null}: {
        name?: string;
        value?: string | null;
        cardinality?: string;
        instructions?: string | null;
    } = {}
): Record<string, unknown> {
    const attribute = Attribute.callKwargs({
        name: name,
        value: value,
        cardinality: cardinality,
        instructions: instructions
    });
    return attribute.asdict(clause).toJs({dict_converter: Object.fromEntries});
}

// @uri, @cardinality, @instructions
export function createClassificationFacet(
    clause: string,
    {value = null, system = null, uri = null, cardinality = "required", instructions = null}: {
        value?: string | null;
        system?: string | null;
        uri?: string | null;
        cardinality?: string;
        instructions?: string | null;
    } = {}
): Record<string, unknown> {
    const classification = Classification.callKwargs({
        value: value,
        system: system,
        uri: uri,
        cardinality: cardinality,
        instructions: instructions
    });
    return classification.asdict(clause).toJs({dict_converter: Object.fromEntries});
}

// @relation, @cardinality, @instructions
export function createPartOfFacet(
    clause: string,
    {name = "IFCWALL", predefinedType = null, relation = null, cardinality = "required", instructions = null}: {
        name?: string;
        predefinedType?: string | null;
        relation?: string | null;
        cardinality?: string;
        instructions?: string | null;
    } = {}
): Record<string, unknown> {
    const part_of = PartOf.callKwargs({
        name: name,
        predefinedType: predefinedType,
        relation: relation,
        cardinality: cardinality,
        instructions: instructions
    });
    return part_of.asdict(clause).toJs({dict_converter: Object.fromEntries});
}

// @dataType, @uri, @cardinality, @instructions
export function createPropertyFacet(
    clause: string,
    {
        propertySet = "Property_Set",
        baseName = "propertyName",
        value = null,
        dataType = null,
        uri = null,
        cardinality = "required",
        instructions = null
    }: {
        propertySet?: string;
        baseName?: string;
        value?: string | null;
        dataType?: string | null;
        uri?: string | null;
        cardinality?: string;
        instructions?: string | null;
    } = {}
): Record<string, unknown> {
    const property = Property.callKwargs({
        propertySet: propertySet,
        baseName: baseName,
        value: value,
        dataType: dataType,
        uri: uri,
        cardinality: cardinality,
        instructions: instructions
    });
    return property.asdict(clause).toJs({dict_converter: Object.fromEntries});
}

// @uri, @cardinality, @instructions
export function createMaterialFacet(
    clause: string,
    {value = null, uri = null, cardinality = "required", instructions = null}: {
        value?: string | null;
        uri?: string | null;
        cardinality?: string;
        instructions?: string | null;
    } = {}
): Record<string, unknown> {
    const material = Material.callKwargs({
        value: value,
        uri: uri,
        cardinality: cardinality,
        instructions: instructions
    });
    return material.asdict(clause).toJs({dict_converter: Object.fromEntries});
}

// Helper function to convert date to ISO format string
export function formatDate(date?: string | number | Date | null): string | null {
    if (!date) return null;
    const d = new Date(date);
    return d.toISOString().split('T')[0];
}

// Expose interface
export const API = {
    "createIDS": createIDS,
    "openIDS": openIDS,
    "validateIDS": validateIDS,
    "exportIDS": exportIDS,
    "createSpecification": createSpecification,
    "createEntityFacet": createEntityFacet,
    "createAttributeFacet": createAttributeFacet,
    "createClassificationFacet": createClassificationFacet,
    "createPartOfFacet": createPartOfFacet,
    "createPropertyFacet": createPropertyFacet,
    "createMaterialFacet": createMaterialFacet,
};
