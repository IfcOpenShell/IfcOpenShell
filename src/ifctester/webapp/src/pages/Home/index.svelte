<script>
    import * as IDS from "$src/modules/api/ids.svelte.js";
    import AppHeader from "$src/components/AppHeader.svelte";
    import AppRibbon from "$src/components/AppRibbon.svelte";
    import AppToolbar from "$src/components/AppToolbar.svelte";
    import IdsTabs from "$src/components/IdsTabs.svelte";
    import IdsMetadataEditor from "./IdsMetadataEditor.svelte";
    import SpecificationEditor from "./SpecificationEditor.svelte";
    import ApplicabilityPanel from "./ApplicabilityPanel.svelte";
    import RequirementsPanel from "./RequirementsPanel.svelte";
    import IdsViewer from "./IdsViewer.svelte";
    import SplashScreen from "$src/components/SplashScreen.svelte";
    import { Toaster } from "$lib/components/ui/sonner";
    import { error, success } from "$src/modules/utils/toast.svelte.js";
    import {onMount} from "svelte";
    import * as DropdownMenu from "$lib/components/ui/dropdown-menu";

    let activeDocument = $derived(IDS.Module.activeDocument ? IDS.Module.documents[IDS.Module.activeDocument] : null);
    let documentState = $derived(IDS.Module.activeDocument ? IDS.Module.states[IDS.Module.activeDocument] : null);
    let activeSpecification = $derived(activeDocument && documentState?.activeSpecification !== null && activeDocument.specifications?.specification ? 
        activeDocument.specifications.specification[documentState.activeSpecification] : null);
    
    async function addNewSpecification() {
        if (!IDS.Module.activeDocument) return;
        await IDS.createSpecification(IDS.Module.activeDocument);

        // Switch to "info" tab
        IDS.setDocumentState(IDS.Module.activeDocument, { activeTab: 'info' });
    }
    
    async function importSpecification(sourceDocId, specIndex) {
        if (!IDS.Module.activeDocument || !IDS.Module.documents[sourceDocId]) return;
        
        try {
            const sourceDoc = IDS.Module.documents[sourceDocId];
            const sourceSpec = sourceDoc.specifications?.specification?.[specIndex];
            
            if (!sourceSpec) {
                error('Specification not found');
                return;
            }
            
            // Create a deep copy of the specification
            const specCopy = JSON.parse(JSON.stringify(sourceSpec));
            
            // Add the copied specification to the current document
            IDS.Module.documents[IDS.Module.activeDocument].specifications.specification.push(specCopy);
            
            // Switch to the newly created specification and info tab
            const currentDoc = IDS.Module.documents[IDS.Module.activeDocument];
            const newSpecIndex = (currentDoc.specifications?.specification?.length || 1) - 1;
            IDS.setDocumentState(IDS.Module.activeDocument, { 
                activeSpecification: newSpecIndex,
                activeTab: 'info'
            });
            
            success(`Specification "${sourceSpec['@name'] || 'Unnamed'}" imported successfully`);
        } catch (err) {
            console.error('Error importing specification:', err);
            error(`Failed to import specification: ${err.message}`);
        }
    }
    
    function selectSpecification(index) {
        if (IDS.Module.activeDocument) {
            IDS.setDocumentState(IDS.Module.activeDocument, { activeSpecification: index });
        }
    }
    
    async function deleteSpecification(specIndex) {
        if (!IDS.Module.activeDocument) return;
        await IDS.deleteSpecification(IDS.Module.activeDocument, specIndex);
    }
    
    async function exportIDS() {
        if (!IDS.Module.activeDocument) {
            error('No document to export');
            return;
        }
        
        try {
            await IDS.exportDocument(IDS.Module.activeDocument);
            success('IDS document exported successfully');
        } catch (err) {
            console.error('Error exporting IDS:', err);
            error('Error exporting IDS: ' + err.message);
        }
    }
</script>

{#if IDS.Module.status != "ready"}
    <SplashScreen />
{/if}
<div class="app">
    <AppHeader />
    <div class="main-body">
        <AppToolbar />
        <div class="main-content">
        {#if Object.keys(IDS.Module.documents).length > 0}
            <IdsTabs />
        {/if}
        <div class="ids-builder">
            {#if IDS.Module.activeDocument && documentState?.viewMode !== 'viewer'}
                <div class="ids-sidebar">
                    <div class="sidebar-header">
                        <h3>Specifications</h3>
                        <DropdownMenu.Root>
                            <DropdownMenu.Trigger class="cta-btn">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="12" y1="5" x2="12" y2="19"></line>
                                    <line x1="5" y1="12" x2="19" y2="12"></line>
                                </svg>
                                New
                            </DropdownMenu.Trigger>
                            <DropdownMenu.Content class="w-56">
                                <DropdownMenu.Item onclick={addNewSpecification}>
                                    <svg class="mr-2 h-4 w-4" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                                        <polyline points="14,2 14,8 20,8"></polyline>
                                    </svg>
                                    Create Specification
                                </DropdownMenu.Item>
                                <DropdownMenu.Sub>
                                    <DropdownMenu.SubTrigger>
                                        <svg class="mr-2 h-4 w-4" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                            <polyline points="14,2 14,8 20,8"></polyline>
                                            <path d="m9 15 2 2 4-4"></path>
                                        </svg>
                                        Import from IDS
                                    </DropdownMenu.SubTrigger>
                                    <DropdownMenu.SubContent class="w-64 max-h-64 overflow-y-auto">
                                        {#each Object.entries(IDS.Module.documents) as [docId, doc]}
                                            {#if docId !== IDS.Module.activeDocument && doc.specifications?.specification?.length > 0}
                                                <DropdownMenu.Label class="font-medium text-xs text-muted-foreground px-2 py-1 truncate">
                                                    {doc.info?.title || 'Untitled Document'}
                                                </DropdownMenu.Label>
                                                {#each doc.specifications.specification as spec, specIndex}
                                                    <DropdownMenu.Item onclick={() => importSpecification(docId, specIndex)}>
                                                        <svg class="mr-2 h-3 w-3" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                                                            <polyline points="14,2 14,8 20,8"></polyline>
                                                        </svg>
                                                        <span class="truncate text-sm">
                                                            {spec['@name'] || `Specification ${specIndex + 1}`}
                                                        </span>
                                                    </DropdownMenu.Item>
                                                {/each}
                                                {#if Object.entries(IDS.Module.documents).filter(([id, d]) => id !== IDS.Module.activeDocument && d.specifications?.specification?.length > 0).indexOf([docId, doc]) < Object.entries(IDS.Module.documents).filter(([id, d]) => id !== IDS.Module.activeDocument && d.specifications?.specification?.length > 0).length - 1}
                                                    <DropdownMenu.Separator />
                                                {/if}
                                            {/if}
                                        {/each}
                                        {#if Object.entries(IDS.Module.documents).filter(([docId, doc]) => docId !== IDS.Module.activeDocument && doc.specifications?.specification?.length > 0).length === 0}
                                            <DropdownMenu.Item disabled>
                                                <span class="text-sm">No specifications available to import</span>
                                            </DropdownMenu.Item>
                                        {/if}
                                    </DropdownMenu.SubContent>
                                </DropdownMenu.Sub>
                            </DropdownMenu.Content>
                        </DropdownMenu.Root>
                    </div>
                    <div class="specifications-list scrollbar">
                        <div class="spec-item" class:active={documentState?.activeSpecification === null} onclick={() => { if (IDS.Module.activeDocument) IDS.setDocumentState(IDS.Module.activeDocument, { activeSpecification: null }); }}>
                            <span class="spec-icon">ℹ️</span>
                            <span class="spec-name">IDS Information</span>
                        </div>
                        {#if activeDocument?.specifications?.specification}
                            {#each activeDocument.specifications.specification as spec, index}
                                <div class="spec-item" class:active={documentState?.activeSpecification === index} onclick={() => selectSpecification(index)}>
                                    <span class="spec-icon">📄</span>
                                    <span class="spec-name">{spec["@name"] || "Specification " + (index + 1)}</span>
                                    <button class="btn-delete" onclick={() => deleteSpecification(index)}>
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M18 6L6 18M6 6l12 12"></path>
                                        </svg>
                                    </button>
                                </div>
                            {/each}
                        {/if}
                    </div>
                </div>
            {/if}
            <div class="main-panel" class:full-width={!IDS.Module.activeDocument} class:scrollbar={true}>
                {#if !IDS.Module.activeDocument}
                    <div class="no-document">
                        <div class="no-document-icon"></div>
                        <button class="btn" onclick={() => IDS.createDocument()}>New IDS</button>
                        <button class="btn" onclick={() => IDS.openDocument()}>Open IDS</button>
                    </div>
                {:else}
                    <!-- Editor/Viewer Toggle -->
                    <div class="view-mode-toggle">
                        <button class="toggle-btn" class:active={documentState?.viewMode === 'editor'} onclick={() => IDS.setDocumentState(IDS.Module.activeDocument, { viewMode: 'editor', auditReport: null })}>
                            Editor
                        </button>
                        <button class="toggle-btn" class:active={documentState?.viewMode === 'viewer'} onclick={() => IDS.setDocumentState(IDS.Module.activeDocument, { viewMode: 'viewer', auditReport: null })}>
                            Viewer
                        </button>
                    </div>

                    {#if documentState?.viewMode === 'viewer'}
                        <IdsViewer />
                    {:else if documentState?.activeSpecification === null}
                        <IdsMetadataEditor />
                    {:else}
                        <div class="specification-editor">
                            <div class="spec-header">
                                <h2>{activeSpecification ? activeSpecification["@name"] || "Specification" : "Specification"}</h2>
                                <div class="spec-tabs">
                                    <button class="btn tab-btn" class:active={documentState?.activeTab === 'info'} onclick={() => IDS.setDocumentState(IDS.Module.activeDocument, { activeTab: 'info' })}>Info</button>
                                    <button class="btn tab-btn" class:active={documentState?.activeTab === 'applicability'} onclick={() => IDS.setDocumentState(IDS.Module.activeDocument, { activeTab: 'applicability' })}>Applicability</button>
                                    <button class="btn tab-btn" class:active={documentState?.activeTab === 'requirements'} onclick={() => IDS.setDocumentState(IDS.Module.activeDocument, { activeTab: 'requirements' })}>Requirements</button>
                                </div>
                            </div>
                            
                            {#if documentState?.activeTab === 'info'}
                                <SpecificationEditor />
                            {:else if documentState?.activeTab === 'applicability'}
                                <ApplicabilityPanel activeTab />
                            {:else if documentState?.activeTab === 'requirements'}
                                <RequirementsPanel activeTab />
                            {/if}
                        </div>
                    {/if}
                {/if}
            </div>
        </div>
    </div>
    </div>
    <AppRibbon />
</div>

<Toaster position="top-center" />
