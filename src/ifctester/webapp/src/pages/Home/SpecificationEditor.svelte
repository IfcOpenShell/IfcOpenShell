<script lang="ts">
    import * as IDS from "$src/modules/api/ids.svelte";
    import type { DocumentState, IdsCardinality, IdsDocument, Specification } from "$src/types/ids";
    
    let activeDocument = $derived(
        IDS.Module.activeDocument ? (IDS.Module.documents[IDS.Module.activeDocument] as IdsDocument) : null
    );
    let documentState = $derived(
        IDS.Module.activeDocument ? (IDS.Module.states[IDS.Module.activeDocument] as DocumentState) : null
    );
    let activeSpecification = $derived(
        activeDocument && documentState && documentState.activeSpecification !== null && activeDocument.specifications?.specification
            ? (activeDocument.specifications.specification[documentState.activeSpecification] as Specification)
            : null
    );

    const getProp = (prop: string) => {
        const value = (activeSpecification as Record<string, unknown>)?.[prop];
        return typeof value === "string" ? value : "";
    };
    
    const setProp = (prop: string, value: string) => {
        if (!activeSpecification) return;
        (activeSpecification as Record<string, unknown>)[prop] = value;
    };

    const addIfcVersion = (e: Event, version: string) => {
        if (activeSpecification) {
            if (!("@ifcVersion" in activeSpecification)) activeSpecification["@ifcVersion"] = [];
            const target = e.target as HTMLInputElement | null;
            if (target?.checked) {
                if (!activeSpecification["@ifcVersion"]?.includes(version)) {
                    activeSpecification["@ifcVersion"] = [...(activeSpecification["@ifcVersion"] ?? []), version];
                }
            } else if (activeSpecification["@ifcVersion"]) {
                activeSpecification["@ifcVersion"] = activeSpecification["@ifcVersion"].filter(v => v !== version);
            }
        }
    };

    const setUsage = (usage: IdsCardinality) => {
        if (!activeSpecification) return;
        if (!activeSpecification.applicability) activeSpecification.applicability = {};
        
        switch (usage) {
            case 'required':
                activeSpecification.applicability["@minOccurs"] = 1;
                activeSpecification.applicability["@maxOccurs"] = "unbounded";
                break;
            case 'optional':
                activeSpecification.applicability["@minOccurs"] = 0;
                activeSpecification.applicability["@maxOccurs"] = "unbounded";
                break;
            case 'prohibited':
                activeSpecification.applicability["@minOccurs"] = 0;
                activeSpecification.applicability["@maxOccurs"] = 0;
                break;
        }
    };
</script>

<div class="spec-info">
    <div class="form-grid">
        <div class="form-group">
            <label for="spec-name">Name</label>
            <input class="form-input" id="spec-name" type="text" bind:value={() => getProp("@name"), (v) => setProp("@name", v)} placeholder="Enter specification name">
        </div>
        <div class="form-group">
            <label for="spec-identifier">Identifier</label>
            <input class="form-input" id="spec-identifier" type="text" bind:value={() => getProp("@identifier"), (v) => setProp("@identifier", v)} placeholder="Enter identifier">
        </div>
        <div class="form-group">
            <label for="spec-cardinality">Usage</label>
            <select
                class="form-input"
                id="spec-cardinality"
                value={IDS.getSpecUsage(activeSpecification)}
                onchange={(e) => setUsage((e.target as HTMLSelectElement).value as IdsCardinality)}
            >
                <option value="required">Required</option>
                <option value="optional">Optional</option>
                <option value="prohibited">Prohibited</option>
            </select>
        </div>
        <div class="form-group full-width">
            <span class="form-label">IFC Version</span>
            <div class="radio-group">
                <label class="radio-label">
                    <input type="checkbox" value="IFC2X3" checked={activeSpecification?.["@ifcVersion"]?.includes('IFC2X3')} onchange={(e) => addIfcVersion(e, 'IFC2X3')}>
                    IFC2X3
                </label>
                <label class="radio-label">
                    <input type="checkbox" value="IFC4" checked={activeSpecification?.["@ifcVersion"]?.includes('IFC4')} onchange={(e) => addIfcVersion(e, 'IFC4')}>
                    IFC4
                </label>
                <label class="radio-label">
                    <input type="checkbox" value="IFC4X3_ADD2" checked={activeSpecification?.["@ifcVersion"]?.includes('IFC4X3_ADD2')} onchange={(e) => addIfcVersion(e, 'IFC4X3_ADD2')}>
                    IFC4X3_ADD2
                </label>
            </div>
        </div>
        <div class="form-group full-width">
            <label for="spec-description">Description</label>
            <textarea class="form-input" id="spec-description" bind:value={() => getProp("@description"), (v) => setProp("@description", v)} placeholder="Enter description" rows="3"></textarea>
        </div>
        <div class="form-group full-width">
            <label for="spec-instructions">Instructions</label>
            <textarea class="form-input" id="spec-instructions" bind:value={() => getProp("@instructions"), (v) => setProp("@instructions", v)} placeholder="Enter instructions" rows="3"></textarea>
        </div>
    </div>
</div>
