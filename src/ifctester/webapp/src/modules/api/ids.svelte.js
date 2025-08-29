import wasm from "$src/modules/wasm";
import { clearIdsAuditReports } from "./api.svelte.js";
import hyperid from "hyperid";
import {tick} from "svelte";

export let Module = $state({
    documents: [],
    activeDocument: null,
    status: "loading",
    states: {}
});

// Initialize module
wasm.init().then(() => {
    Module.status = "ready";
}).catch((error) => {
    Module.status = "error";
});

const id = hyperid()

export function setDocumentState(docId, updates) {
    if (!Module.states[docId]) {
        Module.states[docId] = {
            activeTab: 'info',
            viewMode: 'editor',
            activeSpecification: null
        };
    }
    Object.assign(Module.states[docId], updates);
}

export async function createDocument() {
    const docId = id();
    const doc = await wasm.createIDS();

    Module.documents[docId] = doc;

    // Initialize document state
    setDocumentState(docId, {});

    // Set as active document
    Module.activeDocument = docId;
}

export async function deleteDocument(id) {
    // Clear any audit reports generated using this IDS document
    clearIdsAuditReports(id);
    
    delete Module.documents[id];
    delete Module.states[id];

    if (Module.activeDocument == id) {
        // If there are other documents, set the first one as active
        if (Object.keys(Module.documents).length > 0) {
            Module.activeDocument = Object.keys(Module.documents)[0];
        } else {
            Module.activeDocument = null;
        }
    }
}

// Normalize (remove xs: prefix) from JSON dict returned from Python
// We need this because the backend exports with xs: prefix, yet expects a dict without prefixes.
function normalizeIdsDict(obj) {
    if (typeof obj !== 'object' || obj === null) return obj;
    
    if (Array.isArray(obj)) {
        return obj.map(normalizeIdsDict);
    }
    
    const result = {};
    for (const [key, value] of Object.entries(obj)) {
        if (key === 'xs:restriction' && Array.isArray(value) && value.length > 0) {
            // Convert xs:restriction array to restriction object
            const restriction = value[0];
            const newRestriction = {};
            
            for (const [restrictionKey, restrictionValue] of Object.entries(restriction)) {
                if (restrictionKey.startsWith('xs:')) {
                    // Remove xs: prefix from keys
                    const newKey = restrictionKey.replace('xs:', '');
                    newRestriction[newKey] = restrictionValue;
                } else {
                    newRestriction[restrictionKey] = restrictionValue;
                }
            }
            
            result['restriction'] = newRestriction;
        } else {
            result[key] = normalizeIdsDict(value);
        }
    }
    
    return result;
}

export async function openDocument() {
    return new Promise((resolve, reject) => {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.ids,.xml';
        
        fileInput.onchange = async (event) => {
            const file = event.target.files[0];
            if (!file) {
                reject(new Error('No file selected'));
                return;
            }
            
            try {
                const reader = new FileReader();
                reader.onload = async (e) => {
                    try {
                        const fileContent = e.target.result;
                        const doc = normalizeIdsDict(await wasm.openIDS(fileContent, false));
                        const docId = id();

                        // Add document to list and set as active
                        Module.documents[docId] = doc;
                        
                        // Initialize document state and switch to viewer mode
                        setDocumentState(docId, { viewMode: 'viewer' });
                        
                        Module.activeDocument = docId;

                        resolve();
                    } catch (error) {
                        reject(error);
                    }
                };
                reader.onerror = () => reject(new Error('Failed to read IDS file'));
                reader.readAsText(file);
            } catch (error) {
                reject(error);
            }
        };
        
        fileInput.oncancel = () => {
            reject(new Error('File selection cancelled'));
        };
        
        // Trigger the file dialog
        fileInput.click();
    });
}

export async function exportActiveDocument() {
    if (!Module.activeDocument) return null;

    const doc = $state.snapshot(Module.documents[Module.activeDocument]);
    const xmlString = await wasm.exportIDS(doc);

    return xmlString;
}

export async function exportDocument(docId) {
    const doc = $state.snapshot(Module.documents[docId]);

    // Validate
    if (doc.specifications.specification.length < 1) {
        throw new Error("Please create at least one specification before exporting the document.");
    }

    const xmlString = await wasm.exportIDS(doc);
    
    // Create and download file
    const blob = new Blob([xmlString], { type: 'application/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${Module.documents[docId].info.title.replace(/[^a-zA-Z0-9]/g, '_')}.ids`;
    a.click();
    URL.revokeObjectURL(url);
}

export async function createSpecification(docId) {
    const spec = await wasm.createSpecification();

    // Add specification to document
    Module.documents[docId].specifications.specification.push(spec);

    // Set as active specification
    if (Module.activeDocument == docId) {
        const state = Module.states[docId];
        state.activeSpecification = Module.documents[docId].specifications.specification.length - 1;
    }
}

export async function deleteSpecification(docId, specId) {
    Module.documents[docId].specifications.specification.splice(specId, 1);

    if (Module.activeDocument == docId) {
        const state = Module.states[docId];
        if (state.activeSpecification == specId) {
            // We need to wait for the next tick here because of Svelte's internal shenanigans
            await tick();
            setDocumentState(docId, { activeSpecification: null });

            // If there are other specifications, set the first one as active
            if (Module.documents[docId].specifications.specification.length > 0) {
                setDocumentState(docId, { activeSpecification: 0 });
            }
        }
    }
}

/**
 * clause: "applicability", "requirements"
 * facet: "entity", "attribute", "classification", "partOf", "property", "material"
*/
export async function createFacet(docId, specId, clause, facet) {
    let facetObj;
    if (facet == "entity") {
        facetObj = await wasm.createEntityFacet(clause, {});
    } else if (facet == "attribute") {
        facetObj = await wasm.createAttributeFacet(clause, {});
    } else if (facet == "classification") {
        facetObj = await wasm.createClassificationFacet(clause, {});
    } else if (facet == "partOf") {
        facetObj = await wasm.createPartOfFacet(clause, {});
    } else if (facet == "property") {
        facetObj = await wasm.createPropertyFacet(clause, {});
    } else if (facet == "material") {
        facetObj = await wasm.createMaterialFacet(clause, {});
    }

    if (!(facet in Module.documents[docId].specifications.specification[specId][clause])) {
        Module.documents[docId].specifications.specification[specId][clause][facet] = [];
    }

    Module.documents[docId].specifications.specification[specId][clause][facet].push(facetObj);
}

export async function deleteFacet(docId, specId, clause, facet, facetId) {
    delete Module.documents[docId].specifications.specification[specId][clause][facet][facetId];
}

export function getSpecUsage(spec) {
    if (!spec?.applicability) return 'required';
    const minOccurs = spec.applicability["@minOccurs"];
    const maxOccurs = spec.applicability["@maxOccurs"];
    
    if (minOccurs === 1 && maxOccurs === "unbounded") return 'required';
    if (minOccurs === 0 && maxOccurs === "unbounded") return 'optional';
    if (minOccurs === 0 && maxOccurs === 0) return 'prohibited';
    return 'required';
};

// Converts facet to human-readable description
export function stringifyFacet(clauseType, facet, facetType, spec) {
    if (!facet) return "";

    const usage = getSpecUsage(spec);
    const descriptions = [];
    
    // Entity facet
    if (facetType === "entity") {
        if (clauseType === "applicability") {
            descriptions.push(`All data where IFC class ${stringifyValue(facet.name)}`);
        } else {
            descriptions.push(`Shall be data where IFC class ${stringifyValue(facet.name)}`);
        }

        if (facet.predefinedType) {
            descriptions.push(`and type ${stringifyValue(facet.predefinedType)}`);
        }
    }

    // Attribute facet
    else if (facetType === "attribute") {
        if (clauseType === "applicability") {
            descriptions.push(`All data where attribute ${stringifyValue(facet.name)}`);
        } else {
            descriptions.push(`Shall be data where attribute ${stringifyValue(facet.name)}`);
        }
        descriptions.push(`and value ${stringifyValue(facet.value)}`);
    }

    // Property facet
    else if (facetType === "property") {
        if (clauseType === "applicability") {
            descriptions.push(`Elements where property ${stringifyValue(facet.baseName)}`);
        } else {
            descriptions.push(`Shall be elements where property ${stringifyValue(facet.baseName)}`);
        }
        if (facet.value) {
            descriptions.push(`and value ${stringifyValue(facet.value)}`);
        }
        descriptions.push(`and dataset ${stringifyValue(facet.propertySet)}`);
    }

    // Classification facet
    else if (facetType === "classification") {
        if (clauseType === "applicability") {
            descriptions.push(`All data where classification system ${stringifyValue(facet.system)}`);
        } else {
            descriptions.push(`Shall be data where classification system ${stringifyValue(facet.system)}`);
        }
        if (facet.value) {
            descriptions.push(`and classification ${stringifyValue(facet.value)}`);
        }
    }

    // Material facet
    else if (facetType === "material") {
        if (clauseType === "applicability") {
            descriptions.push(`All data where material ${stringifyValue(facet.value)}`);
        } else {
            descriptions.push(`Shall be data where material ${stringifyValue(facet.value)}`);
        }
    }

    // PartOf facet
    else if (facetType === "partOf") {
        if (clauseType === "applicability") {
            descriptions.push(`An element with an **${facet['@relation']}** relationship`);

            if (facet.name) {
                descriptions.push(`with an entity where IFC class ${stringifyValue(facet.name)}`);
            }
        } else {
            descriptions.push(`An element shall have an **${facet['@relation']}** relationship`);

            if (facet.name) {
                descriptions.push(`with an entity where IFC class ${stringifyValue(facet.name)}`);
            }
            if (facet.predefinedType) {
                descriptions.push(`and predefined type ${stringifyValue(facet.predefinedType)}`);
            }
        }
    }

    let combined = descriptions.join(" ");

    // Post-process for prohibited and optional requirements
    let isProhibited = false;

    if (usage == "prohibited") isProhibited = !isProhibited;
    if (clauseType == "requirements" && "@cardinality" in facet && facet["@cardinality"] == "prohibited") isProhibited = !isProhibited;
    
    if (isProhibited)
        combined = combined.replace("Shall", "Shall not").replace("shall", "shall not");

    if (clauseType == "requirements" && "@cardinality" in facet && facet["@cardinality"] == "optional")
        combined = combined.replace("Shall", "May").replace("shall", "may");
    
    return renderFacetString(combined);
}

// Converts value objects to human-readable strings
function stringifyValue(value) {
    if (!value) return "is provided";
    if (value.simpleValue) return `is **${value.simpleValue}**`;
    if (value.restriction) return stringifyRestriction(value.restriction);
    return "";
}

// Converts restriction objects to human-readable strings
function stringifyRestriction(restriction) {
    if (!restriction) return "";
    
    // Handle enumeration
    if (restriction.enumeration && Array.isArray(restriction.enumeration)) {
        const values = restriction.enumeration.map(item => `**${item['@value']}**` || '').filter(v => v);
        return values.length > 0 ? `is one of ${values.join(", ")}` : "has enumeration restriction";
    }
    
    // Handle pattern
    if (restriction.pattern && Array.isArray(restriction.pattern) && restriction.pattern.length > 0) {
        const pattern = `\`${restriction.pattern[0]['@value']}\`` || '';
        return pattern ? `matches pattern ${pattern}` : "has pattern restriction";
    }
    
    // Handle length restrictions
    if (restriction.length && Array.isArray(restriction.length) && restriction.length.length > 0) {
        const length = `**${restriction.length[0]['@value']}**` || '';
        return length ? `has length ${length}` : "has length restriction";
    }
    
    // Handle range restrictions
    if (restriction.minInclusive || restriction.maxInclusive || 
        restriction.minExclusive || restriction.maxExclusive) {
        const parts = [];
        if (restriction.minInclusive && restriction.minInclusive.length > 0) {
            parts.push(`**≥ ${restriction.minInclusive[0]['@value'] || ''}**`);
        }
        if (restriction.maxInclusive && restriction.maxInclusive.length > 0) {
            parts.push(`**≤ ${restriction.maxInclusive[0]['@value'] || ''}**`);
        }
        if (restriction.minExclusive && restriction.minExclusive.length > 0) {
            parts.push(`**> ${restriction.minExclusive[0]['@value'] || ''}**`);
        }
        if (restriction.maxExclusive && restriction.maxExclusive.length > 0) {
            parts.push(`**< ${restriction.maxExclusive[0]['@value'] || ''}**`);
        }
        return parts.length > 0 ? "is in range " + parts.join(", ") : "has range restriction";
    }
    
    // Handle length range restrictions
    if (restriction.minLength || restriction.maxLength) {
        const parts = [];
        if (restriction.minLength && restriction.minLength.length > 0) {
            parts.push(`**min length ${restriction.minLength[0]['@value'] || ''}**`);
        }
        if (restriction.maxLength && restriction.maxLength.length > 0) {
            parts.push(`**max length ${restriction.maxLength[0]['@value'] || ''}**`);
        }
        return parts.length > 0 ? "has " + parts.join(", ") : "has length range restriction";
    }
    
    return "has complex restriction";
}

function renderFacetString(text) {
    // Convert **text** to <strong>text</strong>
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Convert `text` to <code>text</code>
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    return text;
}