<script lang="ts">
    import * as IDS from "$src/modules/api/ids.svelte";
    import type { IdsDocument } from "$src/types/ids";

    function switchDocument(docId: string) {
        IDS.Module.activeDocument = docId;
    }
    
    function closeDocument(docId: string) {
        IDS.deleteDocument(docId);
    }

    const handleActivation = (event: KeyboardEvent, action: () => void) => {
        if (event.currentTarget !== event.target) return;
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            action();
        }
    };
</script>

<div class="ids-tabs">
    {#each Object.entries(IDS.Module.documents) as [docId, doc]}
        <div 
            class="ids-tab" 
            class:active={IDS.Module.activeDocument === docId}
            role="button"
            tabindex="0"
            onclick={() => switchDocument(docId)}
            onkeydown={(event) => handleActivation(event, () => switchDocument(docId))}
            aria-label={(doc as IdsDocument).info.title || "Untitled"}
        >
            <span class="tab-title">{(doc as IdsDocument).info.title || "Untitled"}</span>
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
