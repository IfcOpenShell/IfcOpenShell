<script lang="ts">
    import * as IDS from "$src/modules/api/ids.svelte";
    import FacetEditor from './FacetEditor.svelte';
    import CreateFacetDropdown from "$src/components/CreateFacetDropdown.svelte";
    import type { DocumentState, Facet, IdsDocument, Specification } from "$src/types/ids";

    type FacetType = "entity" | "attribute" | "classification" | "partOf" | "property" | "material";

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

    async function addFacet(facetType: FacetType) {
        if (!activeSpecification || !documentState || !IDS.Module.activeDocument) return;
        
        await IDS.createFacet(
            IDS.Module.activeDocument, 
            documentState.activeSpecification ?? 0,
            "requirements",
            facetType
        );
    }
    
    async function removeFacet(facetType: FacetType, facetIndex: number) {
        if (!activeSpecification || !documentState || !IDS.Module.activeDocument) return;
        
        await IDS.deleteFacet(
            IDS.Module.activeDocument, 
            documentState.activeSpecification ?? 0,
            "requirements",
            facetType,
            facetIndex
        );
    }

    let requirementEntries = $derived(
        activeSpecification?.requirements
            ? (Object.entries(activeSpecification.requirements).filter(([, facets]) =>
                  Array.isArray(facets)
              ) as Array<[FacetType, Facet[]]>)
            : []
    );
</script>

<div class="restrictions-panel">
    <div class="restrictions-header">
        <h3>Requirements</h3>
        <CreateFacetDropdown {addFacet} />
    </div>
    <div class="restrictions-list">
        {#if activeSpecification && requirementEntries.length > 0}
            {#each requirementEntries as [facetType, facets]}
                {#each facets as facet, index}
                    <FacetEditor 
                        bind:facet={facets[index]} 
                        {facetType} 
                        specification={activeSpecification}
                        activeTab="requirements" 
                        {removeFacet} 
                        {index}
                    />
                {/each}
            {/each}
        {/if}
    </div>
</div>
