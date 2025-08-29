<script>
    import * as IDS from "$src/modules/api/ids.svelte.js";
    import FacetEditor from './FacetEditor.svelte';
    import CreateFacetDropdown from "$src/components/CreateFacetDropdown.svelte";

    let { activeTab } = $props();

    let activeDocument = $derived(IDS.Module.activeDocument ? IDS.Module.documents[IDS.Module.activeDocument] : null);
    let documentState = $derived(IDS.Module.activeDocument ? IDS.Module.states[IDS.Module.activeDocument] : null);
    let activeSpecification = $derived(activeDocument && documentState?.activeSpecification !== null && activeDocument.specifications?.specification ? 
        activeDocument.specifications.specification[documentState.activeSpecification] : null);

    async function addFacet (facetType) {
        if (!activeSpecification) return;
        
        await IDS.createFacet(
            IDS.Module.activeDocument, 
            documentState.activeSpecification, 
            "requirements",
            facetType
        );
    }
    
    async function removeFacet(facetType, facetIndex) {
        if (!activeSpecification) return;
        
        await IDS.deleteFacet(
            IDS.Module.activeDocument, 
            documentState.activeSpecification, 
            "requirements",
            facetType,
            facetIndex
        );
    }
</script>

<div class="restrictions-panel">
    <div class="restrictions-header">
        <h3>Requirements</h3>
        <CreateFacetDropdown {addFacet} />
    </div>
    <div class="restrictions-list">
        {#if activeSpecification?.requirements}
            {#each Object.entries(activeSpecification.requirements) as [facetType, facets]}
                {#each facets as facet, index}
                    <FacetEditor 
                        bind:facet={facets[index]} 
                        {facetType} 
                        specification={activeSpecification}
                        activeTab="requirements" 
                        {removeFacet} 
                        {index}
                        key={`${activeDocument}-${documentState?.activeSpecification}-requirements-${facetType}-${index}`}
                    />
                {/each}
            {/each}
        {/if}
    </div>
</div>