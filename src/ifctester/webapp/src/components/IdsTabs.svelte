<script>
    import * as IDS from "$src/modules/api/ids.svelte.js";

    function switchDocument(docId) {
        IDS.Module.activeDocument = docId;
    }
    
    function closeDocument(docId) {
        IDS.deleteDocument(docId);
    }
</script>

<div class="ids-tabs">
    {#each Object.entries(IDS.Module.documents) as [docId, doc]}
        <div 
            class="ids-tab" 
            class:active={IDS.Module.activeDocument === docId}
            onclick={() => switchDocument(docId)}
            aria-label={doc.info.title || "Untitled"}
        >
            <span class="tab-title">{doc.info.title || "Untitled"}</span>
            <button 
                class="tab-close" 
                onclick={(e) => { e.stopPropagation(); closeDocument(docId); }}
                aria-label="Close document"
            >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"></path>
                </svg>
            </button>
        </div>
    {/each}
    <div class="filler-tab"></div>
</div>