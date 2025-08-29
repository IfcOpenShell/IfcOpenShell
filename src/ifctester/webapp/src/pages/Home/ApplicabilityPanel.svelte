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
            "applicability", 
            facetType
        );
    }
    
    async function removeFacet(facetType, facetIndex) {
        if (!activeSpecification) return;
        
        await IDS.deleteFacet(
            IDS.Module.activeDocument, 
            documentState.activeSpecification, 
            "applicability", 
            facetType,
            facetIndex
        );
    }
</script>

<div class="restrictions-panel">
    <div class="restrictions-header">
        <h3>Applicability</h3>
        <CreateFacetDropdown {addFacet} />
    </div>
    <div class="restrictions-list">
        {#if activeSpecification?.applicability}
            {#each Object.entries(activeSpecification.applicability) as [facetType, facets]}
                {#if facetType !== "@minOccurs" && facetType !== "@maxOccurs"}
                    {#each facets as facet, index}
                        <FacetEditor 
                            bind:facet={facets[index]} 
                            {facetType} 
                            specification={activeSpecification}
                            activeTab="applicability" 
                            {removeFacet} 
                            {index}
                            key={`${activeDocument}-${documentState?.activeSpecification}-applicability-${facetType}-${index}`}
                        />
                    {/each}
                {/if}
            {/each}
        {/if}
    </div>
</div>