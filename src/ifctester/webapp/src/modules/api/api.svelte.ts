import wasm from "$src/modules/wasm";
import * as IDS from "$src/modules/api/ids.svelte";
import hyperid from "hyperid";
import type { AuditReport, AuditReportData } from "$src/types/report";
import type { IdsDocument } from "$src/types/ids";

type AutocompletionState = {
    entityClasses: string[];
    materialCategories: string[];
    classificationSystems: Record<string, { source: string; tokens: string[] | null }>;
    dataTypes: string[];
    isLoaded: boolean;
};

type IfcModel = {
    id: string;
    fileName: string;
    fileSize: number;
    loadedAt: Date;
};

type IfcModelState = {
    models: IfcModel[];
    isLoading: boolean;
    audits: AuditReport[];
};

export const Autocompletions: AutocompletionState = $state({
    entityClasses: [],
    materialCategories: [],
    classificationSystems: {},
    dataTypes: [],
    isLoaded: false
});

export const IFCModels: IfcModelState = $state({
    models: [],
    isLoading: false,
    audits: []
});

const id: () => string = hyperid();

// Preload autocompletions on initialization
wasm.init().then(async () => {
    await preloadAutocompletions();
});

export async function preloadAutocompletions() {
    try {
        const schemas = ["IFC2X3", "IFC4"]; // TODO: IFC4X3 is excluded for now because of an error
        
        // Entity classes
        const entitySets = await Promise.all(
            schemas.map(schema => wasm.getAllEntityClasses(schema))
        ) as string[][];
        const allEntities = new Set<string>();
        for (const entities of entitySets) {
            for (const entity of entities) {
                allEntities.add(entity.toUpperCase());
            }
        }
        
        // Data types
        const dataTypeSets = await Promise.all(
            schemas.map(schema => wasm.getAllDataTypes(schema))
        ) as Record<string, string>[];
        const allDataTypes = new Set<string>();
        for (const dataTypes of dataTypeSets) {
            for (const dataType of Object.keys(dataTypes as Record<string, string>)) {
                allDataTypes.add(dataType);
            }
        }
        
        // Material categories and Classification systems
        const [materialCategories, classificationSystems] = await Promise.all([
            wasm.getMaterialCategories(),
            wasm.getStandardClassificationSystems()
        ]) as [string[], AutocompletionState["classificationSystems"]];
        
        // Cache autocompletions
        Autocompletions.entityClasses = Array.from(allEntities).sort();
        Autocompletions.materialCategories = materialCategories;
        Autocompletions.classificationSystems = classificationSystems;
        Autocompletions.dataTypes = Array.from(allDataTypes).sort();
        Autocompletions.isLoaded = true;
        
        console.log('Autocompletions preloaded');
    } catch (error) {
        console.error('Failed to preload autocompletions:', error);
    }
}

export async function getPredefinedTypes(schema: string, entity: string) {
    return await wasm.getPredefinedTypes(schema, entity);
}

export async function getEntityAttributes(schema: string, entity: string) {
    return await wasm.getEntityAttributes(schema, entity);
}

export async function getApplicablePsets(schema: string, entity: string, predefinedType = '') {
    return await wasm.getApplicablePsets(schema, entity, predefinedType);
}

export function getEntityClasses() {
    return Autocompletions.entityClasses;
}

export function getMaterialCategories() {
    return Autocompletions.materialCategories;
}

export function getClassificationSystems() {
    return Autocompletions.classificationSystems;
}

export function getDataTypes() {
    return Autocompletions.dataTypes;
}

export async function loadIfc(file: File): Promise<IfcModel> {
    try {
        IFCModels.isLoading = true;
        
        const arrayBuffer = await file.arrayBuffer();
        const uint8Array = new Uint8Array(arrayBuffer);
        
        // Load IFC model
        const ifcId = await wasm.loadIfc(Array.from(uint8Array)) as string;
        
        // Add to models list
        const model: IfcModel = {
            id: ifcId,
            fileName: file.name,
            fileSize: file.size,
            loadedAt: new Date()
        };
        IFCModels.models = [...IFCModels.models, model];
        
        console.log(`IFC model "${file.name}" loaded with ID: ${ifcId}`);
        return model;
    } catch (error) {
        console.error('Failed to load IFC model:', error);
        throw error;
    } finally {
        IFCModels.isLoading = false;
    }
}

export async function unloadIfc(modelId: string) {
    try {
        // Unload model
        await wasm.unloadIfc(modelId);
        
        // Remove from models list
        IFCModels.models = IFCModels.models.filter(model => model.id !== modelId);
        
        console.log(`IFC model with ID ${modelId} unloaded`);
    } catch (error) {
        console.error('Failed to unload IFC model:', error);
        throw error;
    }
}

export async function auditIfc(modelId: string, idsData: string | Uint8Array | ArrayBuffer) {
    try {
        let idsBytes: Uint8Array;
        if (typeof idsData === 'string') {
            idsBytes = new TextEncoder().encode(idsData);
        } else if (idsData instanceof ArrayBuffer) {
            idsBytes = new Uint8Array(idsData);
        } else {
            idsBytes = idsData;
        }
        
        // Run audit
        const auditResult = await wasm.auditIfc(modelId, idsBytes) as { json: AuditReportData; html: string };
        
        console.log(`Audit completed for model ${modelId}`);
        return auditResult;
    } catch (error) {
        console.error('Failed to audit IFC model:', error);
        throw error;
    }
}

export function getLoadedModels() {
    return IFCModels.models;
}

export async function openIfc() {
    return new Promise<void>((resolve, reject) => {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.ifc';
        
        fileInput.onchange = async (event) => {
            const target = event.target as HTMLInputElement | null;
            const file = target?.files?.[0];
            if (!file) {
                reject(new Error('No file selected'));
                return;
            }
            
            // Check if it's an IFC file
            if (!file.name.toLowerCase().endsWith('.ifc')) {
                reject(new Error('Please select a valid IFC file (.ifc)'));
                return;
            }
            
            try {
                await loadIfc(file);
                resolve();
            } catch (error) {
                reject(error);
            }
        };
        
        fileInput.onerror = () => reject(new Error('Failed to open file picker'));
        fileInput.click();
    });
}

export function getIfcById(modelId: string) {
    return IFCModels.models.find(model => model.id === modelId);
}

export function createAuditReport(
    modelId: string,
    document: string,
    auditData: AuditReportData,
    htmlReport: string | null = null
): AuditReport | undefined {
    const model = getIfcById(modelId);
    if (!model) return;
    
    const auditReport: AuditReport = {
        id: id(),
        modelId: modelId,
        modelName: model.fileName,
        document: document,
        date: new Date().toISOString(),
        data: auditData,
        htmlReport: htmlReport
    };
    
    IFCModels.audits.unshift(auditReport);
    return auditReport;
}

export function getAuditReportsForIfc(modelId: string) {
    return IFCModels.audits.filter(audit => audit.modelId === modelId);
}

export function getAuditReportById(auditId: string) {
    return IFCModels.audits.find(audit => audit.id === auditId);
}

export function clearIdsAuditReports(document: string) {
    IFCModels.audits = IFCModels.audits.filter(audit => audit.document !== document);
}

export async function downloadAuditReport(auditId: string) {
    const audit = getAuditReportById(auditId);
    if (!audit || !audit.htmlReport) {
        throw new Error('HTML report not available for this audit');
    }
    
    // Get IDS document title for filename
    let filename = 'report.html';
    if (audit.document && IDS.Module.documents[audit.document]) {
        const doc = IDS.Module.documents[audit.document] as IdsDocument;
        const title = doc.info?.title || 'untitled';
        filename = `report_${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.html`;
    }
    
    const blob = new Blob([audit.htmlReport], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

export async function runAudit() {
    if (IFCModels.models.length === 0) {
        throw new Error('Please load an IFC model first');
    }
    
    if (!IDS.Module.activeDocument) {
        throw new Error('Please create or open an IDS document first');
    }
    
    // Clear previous audit reports
    IFCModels.audits = [];
    
    // Get the active IDS document XML
    const idsXml = await IDS.exportActiveDocument();
    if (!idsXml) {
        throw new Error('Failed to export IDS document');
    }
    
    // Run audit on all loaded models
    let firstAuditReport: AuditReport | undefined;
    for (const model of IFCModels.models) {
        const result = await auditIfc(model.id, idsXml);
        
        // Extract JSON and HTML reports from the result
        const jsonData = result.json || null;
        const htmlReport = result.html || null;
        
        if (!jsonData) {
            continue;
        }
        const auditReport = createAuditReport(model.id, IDS.Module.activeDocument as string, jsonData, htmlReport);
        
        // Store the first audit report to open in viewer
        if (!firstAuditReport) {
            firstAuditReport = auditReport;
        }
    }
    
    // Switch to viewer mode and set the first audit report as active
    if (firstAuditReport && IDS.Module.activeDocument) {
        IDS.setDocumentState(IDS.Module.activeDocument, { 
            viewMode: 'viewer',
            auditReport: firstAuditReport.id
        });
    }
    
    return firstAuditReport;
}
