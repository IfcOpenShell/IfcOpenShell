import wasm from "$src/modules/wasm";
import { clearIdsAuditReports } from "./api.svelte";
import hyperid from "hyperid";
import {tick} from "svelte";
import type { DocumentState, Facet, FacetValue, IdsDocument, IdsCardinality, Restriction, Specification } from "$src/types/ids";

type ModuleState = {
    documents: Record<string, IdsDocument>;
    activeDocument: string | null;
    status: "loading" | "ready" | "error";
    states: Record<string, DocumentState>;
};

export const Module: ModuleState = $state({
    documents: {},
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

const id: () => string = hyperid();

export function setDocumentState(docId: string, updates: Partial<DocumentState>) {
    if (!Module.states[docId]) {
        Module.states[docId] = {
            activeTab: 'info',
            viewMode: 'editor',
            activeSpecification: null,
            auditReport: null
        };
    }
    Object.assign(Module.states[docId], updates);
}

export async function createDocument() {
    const docId = id();
    const doc = await wasm.createIDS() as IdsDocument;

    Module.documents[docId] = doc;

    // Initialize document state
    setDocumentState(docId, {});

    // Set as active document
    Module.activeDocument = docId;
}

export async function deleteDocument(id: string) {
    // Clear any audit reports generated using this IDS document
    clearIdsAuditReports(id);
    
    delete Module.documents[id];
    delete Module.states[id];

    if (Module.activeDocument === id) {
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
function normalizeIdsDict(obj: unknown): unknown {
    if (typeof obj !== 'object' || obj === null) return obj;
    
    if (Array.isArray(obj)) {
        return obj.map(normalizeIdsDict);
    }
    
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj)) {
        if (key === 'xs:restriction' && Array.isArray(value) && value.length > 0) {
            // Convert xs:restriction array to restriction object
            const restriction = value[0] as Record<string, unknown>;
            const newRestriction: Record<string, unknown> = {};
            
            for (const [restrictionKey, restrictionValue] of Object.entries(restriction)) {
                if (restrictionKey.startsWith('xs:')) {
                    // Remove xs: prefix from keys
                    const newKey = restrictionKey.replace('xs:', '');
                    newRestriction[newKey] = restrictionValue;
                } else {
                    newRestriction[restrictionKey] = restrictionValue;
                }
            }
            
            result.restriction = newRestriction;
        } else {
            result[key] = normalizeIdsDict(value);
        }
    }
    
    return result;
}

export async function openDocument() {
    return new Promise<void>((resolve, reject) => {
        const fileInput = document.createElement('input') as HTMLInputElement & {
            oncancel?: ((this: HTMLInputElement, ev: Event) => void) | null;
        };
        fileInput.type = 'file';
        fileInput.accept = '.ids,.xml';
        
        fileInput.onchange = async (event) => {
            const target = event.target as HTMLInputElement | null;
            const file = target?.files?.[0];
            if (!file) {
                reject(new Error('No file selected'));
                return;
            }
            
            try {
                const reader = new FileReader();
                reader.onload = async (e) => {
                    try {
                        const fileContent = (e.target as FileReader).result;
                        const doc = normalizeIdsDict(await wasm.openIDS(String(fileContent), false)) as IdsDocument;
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

export async function exportActiveDocument(): Promise<string | null> {
    if (!Module.activeDocument) return null;

    const doc = $state.snapshot(Module.documents[Module.activeDocument]);
    const xmlString = await wasm.exportIDS(doc as Record<string, unknown>) as string;

    return xmlString;
}

export async function exportDocument(docId: string) {
    const doc = $state.snapshot(Module.documents[docId]);

    // Validate
    if (doc.specifications.specification.length < 1) {
        throw new Error("Please create at least one specification before exporting the document.");
    }

    const xmlString = await wasm.exportIDS(doc as Record<string, unknown>) as string;
    
    // Create and download file
    const blob = new Blob([xmlString], { type: 'application/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const title = Module.documents[docId].info.title || "untitled";
    a.download = `${title.replace(/[^a-zA-Z0-9]/g, '_')}.ids`;
    a.click();
    URL.revokeObjectURL(url);
}

export async function createSpecification(docId: string) {
    const spec = await wasm.createSpecification() as Specification;

    // Add specification to document
    Module.documents[docId].specifications.specification.push(spec);

    // Set as active specification
    if (Module.activeDocument === docId) {
        const state = Module.states[docId];
        state.activeSpecification = Module.documents[docId].specifications.specification.length - 1;
    }
}

export async function deleteSpecification(docId: string, specId: number) {
    Module.documents[docId].specifications.specification.splice(specId, 1);

    if (Module.activeDocument === docId) {
        const state = Module.states[docId];
        if (state.activeSpecification === specId) {
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
export async function createFacet(
    docId: string,
    specId: number,
    clause: "applicability" | "requirements",
    facet: "entity" | "attribute" | "classification" | "partOf" | "property" | "material"
) {
    let facetObj: Facet | undefined;
    if (facet === "entity") {
        facetObj = await wasm.createEntityFacet(clause, {}) as Facet;
    } else if (facet === "attribute") {
        facetObj = await wasm.createAttributeFacet(clause, {}) as Facet;
    } else if (facet === "classification") {
        facetObj = await wasm.createClassificationFacet(clause, {}) as Facet;
    } else if (facet === "partOf") {
        facetObj = await wasm.createPartOfFacet(clause, {}) as Facet;
    } else if (facet === "property") {
        facetObj = await wasm.createPropertyFacet(clause, {}) as Facet;
    } else if (facet === "material") {
        facetObj = await wasm.createMaterialFacet(clause, {}) as Facet;
    }

    if (!facetObj) return;

    const spec = Module.documents[docId].specifications.specification[specId];
    const clauseKey = clause as "applicability" | "requirements";
    if (!spec[clauseKey]) spec[clauseKey] = {};
    if (!(facet in (spec[clauseKey] as Record<string, unknown>))) {
        (spec[clauseKey] as Record<string, unknown>)[facet] = [];
    }

    ((spec[clauseKey] as Record<string, unknown>)[facet] as Facet[]).push(facetObj);
}

export async function deleteFacet(
    docId: string,
    specId: number,
    clause: "applicability" | "requirements",
    facet: "entity" | "attribute" | "classification" | "partOf" | "property" | "material",
    facetId: number
) {
    const spec = Module.documents[docId].specifications.specification[specId];
    const list = (spec[clause] as Record<string, unknown> | undefined)?.[facet] as Facet[] | undefined;
    if (!list) return;
    list.splice(facetId, 1);
}

export function getSpecUsage(spec?: Specification | null): IdsCardinality {
    if (!spec?.applicability) return 'required';
    const minOccurs = spec.applicability["@minOccurs"] as number | undefined;
    const maxOccurs = spec.applicability["@maxOccurs"] as number | "unbounded" | undefined;

    if (minOccurs !== 0) return 'required';
    if (minOccurs === 0 && maxOccurs !== 0) return 'optional';
    if (maxOccurs === 0) return 'prohibited';
    return 'required';
};

// Converts facet to human-readable description
export function stringifyFacet(
    clauseType: "applicability" | "requirements",
    facet: Facet,
    facetType: string,
    spec?: Specification | null
) {
    if (!facet) return "";

    const usage = getSpecUsage(spec);
    const descriptions: string[] = [];
    
    // Entity facet
    if (facetType === "entity") {
        if (clauseType === "applicability") {
            descriptions.push(`All data where IFC class ${stringifyValue(facet.name as FacetValue)}`);
        } else {
            descriptions.push(`Shall be data where IFC class ${stringifyValue(facet.name as FacetValue)}`);
        }

        if (facet.predefinedType) {
            descriptions.push(`and type ${stringifyValue(facet.predefinedType as FacetValue)}`);
        }
    }

    // Attribute facet
    else if (facetType === "attribute") {
        if (clauseType === "applicability") {
            descriptions.push(`All data where attribute ${stringifyValue(facet.name as FacetValue)}`);
        } else {
            descriptions.push(`Shall be data where attribute ${stringifyValue(facet.name as FacetValue)}`);
        }
        descriptions.push(`and value ${stringifyValue(facet.value as FacetValue)}`);
    }

    // Property facet
    else if (facetType === "property") {
        if (clauseType === "applicability") {
            descriptions.push(`Elements where property ${stringifyValue(facet.baseName as FacetValue)}`);
        } else {
            descriptions.push(`Shall be elements where property ${stringifyValue(facet.baseName as FacetValue)}`);
        }
        if (facet.value) {
            descriptions.push(`and value ${stringifyValue(facet.value as FacetValue)}`);
        }
        descriptions.push(`and dataset ${stringifyValue(facet.propertySet as FacetValue)}`);
    }

    // Classification facet
    else if (facetType === "classification") {
        if (clauseType === "applicability") {
            descriptions.push(`All data where classification system ${stringifyValue(facet.system as FacetValue)}`);
        } else {
            descriptions.push(`Shall be data where classification system ${stringifyValue(facet.system as FacetValue)}`);
        }
        if (facet.value) {
            descriptions.push(`and classification ${stringifyValue(facet.value as FacetValue)}`);
        }
    }

    // Material facet
    else if (facetType === "material") {
        if (clauseType === "applicability") {
            descriptions.push(`All data where material ${stringifyValue(facet.value as FacetValue)}`);
        } else {
            descriptions.push(`Shall be data where material ${stringifyValue(facet.value as FacetValue)}`);
        }
    }

    // PartOf facet
    else if (facetType === "partOf") {
        if (clauseType === "applicability") {
            descriptions.push(`An element with an **${String(facet['@relation'] ?? "")}** relationship`);

            if (facet.name) {
                descriptions.push(`with an entity where IFC class ${stringifyValue(facet.name as FacetValue)}`);
            }
        } else {
            descriptions.push(`An element shall have an **${String(facet['@relation'] ?? "")}** relationship`);

            if (facet.name) {
                descriptions.push(`with an entity where IFC class ${stringifyValue(facet.name as FacetValue)}`);
            }
            if (facet.predefinedType) {
                descriptions.push(`and predefined type ${stringifyValue(facet.predefinedType as FacetValue)}`);
            }
        }
    }

    let combined = descriptions.join(" ");

    // Post-process for prohibited and optional requirements
    let isProhibited = false;

    if (usage === "prohibited") isProhibited = !isProhibited;
    if (clauseType === "requirements" && "@cardinality" in facet && facet["@cardinality"] === "prohibited") {
        isProhibited = !isProhibited;
    }
    
    if (isProhibited)
        combined = combined.replace("Shall", "Shall not").replace("shall", "shall not");

    if (clauseType === "requirements" && "@cardinality" in facet && facet["@cardinality"] === "optional")
        combined = combined.replace("Shall", "May").replace("shall", "may");
    
    return renderFacetString(combined);
}

// Converts value objects to human-readable strings
function stringifyValue(value?: FacetValue) {
    if (!value) return "is provided";
    if (value.simpleValue) return `is **${value.simpleValue}**`;
    if (value.restriction) return stringifyRestriction(value.restriction);
    return "";
}

// Converts restriction objects to human-readable strings
function stringifyRestriction(restriction: Restriction) {
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
        return parts.length > 0 ? `is in range ${parts.join(", ")}` : "has range restriction";
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
        return parts.length > 0 ? `has ${parts.join(", ")}` : "has length range restriction";
    }
    
    return "has complex restriction";
}

function renderFacetString(text: string): string {
    // Convert **text** to <strong>text</strong>
    const withStrong = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Convert `text` to <code>text</code>
    const withCode = withStrong.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    return withCode;
}
