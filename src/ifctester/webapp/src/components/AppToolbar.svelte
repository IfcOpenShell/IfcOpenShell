<script>
    import * as Tooltip from "$lib/components/ui/tooltip";
    import { IFCModels, loadIfc, unloadIfc, auditIfc, openIfc, createAuditReport, clearIdsAuditReports, runAudit } from "$src/modules/api/api.svelte.js";
    import * as IDS from "$src/modules/api/ids.svelte.js";
    import { error, success } from "$src/modules/utils/toast.svelte.js";
    import { ChevronRightIcon, LinkIcon, XIcon } from "@lucide/svelte";
    import { Bonsai, connect, disconnect, runAudit as runBonsaiAudit } from "$src/modules/api/bonsai.svelte.js";
    import { onMount } from 'svelte';
    
    let isAuditing = $state(false);
    let activeTab = $state('home');
    let isMinimized = $state(false);
    
    const handleLoadModel = async () => {
        try {
            await openIfc();
            success('IFC model loaded successfully');
        } catch (err) {
            error(`Failed to load IFC model: ${err.message}`);
        }
    };
    
    const handleUnloadModel = async (modelId) => {
        try {
            await unloadIfc(modelId);
        } catch (err) {
            error(`Failed to unload model: ${err.message}`);
        }
    };
    
    const handleRunAudit = async () => {
        try {
            isAuditing = true;
            await runAudit();
            success('Audit completed successfully');
        } catch (err) {
            console.error("Audit failed: ", err);
            error(`Audit failed: check console for details`);
        } finally {
            isAuditing = false;
        }
    };
    
    const handleViewAuditReport = (auditId) => {
        const auditReport = IFCModels.audits.find(audit => audit.id === auditId);
        if (!auditReport) return;
        
        // Switch to the IDS document that was used for this audit
        if (auditReport.document && IDS.Module.documents[auditReport.document]) {
            // Set the correct document as active
            IDS.Module.activeDocument = auditReport.document;
            
            // Set the document state to show the audit report
            IDS.setDocumentState(auditReport.document, { 
                viewMode: 'viewer',
                auditReport: auditId
            });
        }
    };
    
    const formatFileSize = (bytes) => {
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)} ${units[unitIndex]}`;
    };
    
    const handleBonsaiAudit = async () => {
        const auditId = await runBonsaiAudit();
        if (auditId) {
            // Auto-open the report viewer
            handleViewAuditReport(auditId);
        }
    };
    
    onMount(() => {
        if (Bonsai.enabled) {
            activeTab = 'bonsai';
            connect();
        }
    });
</script>

<div class="toolbar">
    <div class="buttons">
        <Tooltip.Provider>
            {#if isMinimized}
                <Tooltip.Root disableHoverableContent="true">
                    <Tooltip.Trigger>
                        <button class="tb-btn expand-btn" onclick={() => isMinimized = false} aria-label="Expand Toolbar">
                            <ChevronRightIcon size={24} />
                        </button>
                    </Tooltip.Trigger>
                    <Tooltip.Content side="right">
                        <p>Expand Toolbar</p>
                    </Tooltip.Content>
                </Tooltip.Root>
            {/if}
            <Tooltip.Root disableHoverableContent="true">
                <Tooltip.Trigger>
                    <button class="tb-btn {activeTab === 'home' ? 'active' : ''}" onclick={() => activeTab = 'home'} aria-label="Home">
                        <svg class="w-6 h-6" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m4 12 8-8 8 8M6 10.5V19a1 1 0 0 0 1 1h3v-3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3h3a1 1 0 0 0 1-1v-8.5"/>
                        </svg>
                    </button>
                </Tooltip.Trigger>
                <Tooltip.Content side="right">
                    <p>Home</p>
                </Tooltip.Content>
            </Tooltip.Root>
            <Tooltip.Root disableHoverableContent="true">
                <Tooltip.Trigger>
                    <button class="tb-btn {activeTab === 'bonsai' ? 'active' : ''}" onclick={() => activeTab = 'bonsai'} aria-label="Bonsai Integration">
                        <svg style="height: 20px;" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="32mm" height="32mm" version="1.1" viewBox="0 0 32 32" xml:space="preserve">
                            <defs><linearGradient id="a" x1="319.66" x2="414.22" y1="725.95" y2="631.1" gradientTransform="matrix(.34384 0 0 .34384 1065.6 -23.668)" gradientUnits="userSpaceOnUse"><stop stop-color="currentColor" offset="0" /><stop stop-color="currentColor" offset="1" /></linearGradient></defs>
                            <g transform="translate(-1274.3 -68)"><g transform="matrix(.89066 0 0 .89066 230.47 -102.44)" clip-rule="evenodd"><path d="m1177.3 192.49c-1.0334-2e-5 -1.8713 0.83759-1.8715 1.871v29.941c0 1.0336 0.8379 1.8716 1.8715 1.8715h19.461c0.4963-1.1e-4 0.9723-0.19737 1.3231-0.54839l7.8162-7.8161c0.7306-0.73081 0.7306-1.9154 0-2.6462l-5.0282-5.0282-2.3818 2.3818 3.9696 3.9696-6.3191 6.3191h-17.344v-26.946l17.321-0.0212 6.3429 6.3581-12.703 12.703-5.5574-5.5574 5.5574-5.5574 4.7635 4.7635 2.3818-2.3818-5.8217-5.8221c-0.7286-0.72842-1.9168-0.72974-2.6467 0l-7.6763 7.6763c-0.706 0.70636-0.733 1.8426-0.061 2.5817l7.7091 7.7091c0.7309 0.80387 1.9905 0.81846 2.7398 0.0317l14.796-14.864c0.7006-0.73553 0.6866-1.8956-0.032-2.614l-7.8253-7.8253c-0.351-0.35081-0.8269-0.54787-1.3231-0.54785z" fill="currentColor" fill-rule="evenodd"/><rect transform="matrix(.14035 0 0 .14035 1172 191.36)" x="-8.2421e-7" y="-1.0518e-16" width="256" height="256" fill="none"/></g></g>
                        </svg>
                    </button>
                </Tooltip.Trigger>
                <Tooltip.Content side="right">
                    <p>Bonsai Integration</p>
                </Tooltip.Content>
            </Tooltip.Root>
        </Tooltip.Provider>
    </div>
    <div class="content scrollbar" style:display={isMinimized ? 'none' : 'block'}>
        <div class="content-header">
            {#if isMinimized}
                <button onclick={() => isMinimized = false} class="open-btn" aria-label="Open Toolbar">
                    <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 10 12 14 8 10m8 0V4h-8v6"/>
                    </svg>
                </button>
            {:else}
                <h1>{activeTab === 'home' ? 'IFC Models' : 'Bonsai Integration'}</h1>
                <button onclick={() => isMinimized = true} aria-label="Minimize Toolbar">
                    <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.99994 10 7 11.9999l1.99994 2M12 5v14M5 4h14c.5523 0 1 .44772 1 1v14c0 .5523-.4477 1-1 1H5c-.55228 0-1-.4477-1-1V5c0-.55228.44772-1 1-1Z"/>
                    </svg>
                </button>
            {/if}
        </div>
        
        <div class="content-body">
            {#if activeTab === 'home'}
            <div class="section">
                <button class="load-btn" onclick={handleLoadModel} disabled={IFCModels.isLoading}>
                    {#if IFCModels.isLoading}
                        <svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 12a9 9 0 11-6.219-8.56"/>
                        </svg>
                        Loading...
                    {:else}
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                            <polyline points="14,2 14,8 20,8"/>
                        </svg>
                        Load IFC Model
                    {/if}
                </button>
            </div>
            
            <!-- IFC Models -->
            {#if IFCModels.models.length > 0}
                <div class="section">
                    <h3>Active Models</h3>
                    <div class="models-list">
                        {#each IFCModels.models as model}
                            <div class="model-item">
                                <div class="model-info">
                                    <Tooltip.Provider>
                                        <Tooltip.Root delayDuration={0}>
                                            <Tooltip.Trigger>
                                                <div class="model-name">{model.fileName}</div>
                                            </Tooltip.Trigger>
                                            <Tooltip.Content>
                                                <p>{model.fileName}</p>
                                            </Tooltip.Content>
                                        </Tooltip.Root>
                                    </Tooltip.Provider>
                                    <div class="model-meta">
                                        <span class="model-size">{formatFileSize(model.fileSize)}</span>
                                    </div>
                                </div>
                                <button class="unload-btn" onclick={() => handleUnloadModel(model.id)} title="Unload model" aria-label="Unload model">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M18 6L6 18M6 6l12 12"/>
                                    </svg>
                                </button>
                            </div>
                        {/each}
                    </div>
                </div>
                
                <div class="section">
                    <button class="audit-btn" onclick={handleRunAudit} disabled={isAuditing || !IDS.Module.activeDocument}>
                        {#if isAuditing}
                            <svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 12a9 9 0 11-6.219-8.56"/>
                            </svg>
                            Running Audit...
                        {:else}
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <polyline points="12,6 12,12 16,14"/>
                            </svg>
                            Run Audit
                        {/if}
                    </button>
                    {#if !IDS.Module.activeDocument}
                        <p class="help-text">Create or open an IDS document to enable auditing</p>
                    {/if}
                </div>
            {:else}
                <div class="empty-state">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                        <polyline points="14,2 14,8 20,8"/>
                    </svg>
                    <p>No IFC models loaded</p>
                    <p class="help-text">Load an IFC model to begin auditing</p>
                </div>
            {/if}
            
            <!-- Audit Reports -->
            {#if IFCModels.audits.length > 0}
                <div class="section">
                    <h3>Audit Reports</h3>
                    <div class="audit-reports">
                        {#each IFCModels.audits as audit}
                            <button class="audit-report-item" onclick={() => handleViewAuditReport(audit.id)} aria-label="View audit report for {audit.modelName}">
                                <div class="report-info">
                                    <Tooltip.Provider>
                                        <Tooltip.Root delayDuration={0}>
                                            <Tooltip.Trigger>
                                                <div class="report-title">{audit.modelName}</div>
                                            </Tooltip.Trigger>
                                            <Tooltip.Content>
                                                <p>{audit.modelName}</p>
                                            </Tooltip.Content>
                                        </Tooltip.Root>
                                    </Tooltip.Provider>
                                    <div class="report-meta">
                                        <span class="report-date">{new Date(audit.date).toLocaleString()}</span>
                                        <span class="report-status {audit.data.status ? 'pass' : 'fail'}">
                                            {audit.data.status ? 'PASS' : 'FAIL'}
                                        </span>
                                    </div>
                                    <div class="report-summary">
                                        {audit.data.total_checks_pass}/{audit.data.total_checks} checks passed
                                    </div>
                                    <div class="report-progress">
                                        <div class="progress-bar-small">
                                            <div class="progress-fill-small" style="width: {audit.data.percent_checks_pass}%"></div>
                                        </div>
                                    </div>
                                </div>
                                <svg class="view-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M9 18l6-6-6-6"/>
                                </svg>
                            </button>
                        {/each}
                    </div>
                </div>
            {/if}
            {:else if activeTab === 'bonsai'}
                {#if !Bonsai.enabled}
                    <div class="empty-state">
                        <svg style="height: 48px;" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="32mm" height="32mm" version="1.1" viewBox="0 0 32 32" xml:space="preserve">
                            <defs><linearGradient id="bonsai-grad" x1="319.66" x2="414.22" y1="725.95" y2="631.1" gradientTransform="matrix(.34384 0 0 .34384 1065.6 -23.668)" gradientUnits="userSpaceOnUse"><stop stop-color="currentColor" offset="0" /><stop stop-color="currentColor" offset="1" /></linearGradient></defs>
                            <g transform="translate(-1274.3 -68)"><g transform="matrix(.89066 0 0 .89066 230.47 -102.44)" clip-rule="evenodd"><path d="m1177.3 192.49c-1.0334-2e-5 -1.8713 0.83759-1.8715 1.871v29.941c0 1.0336 0.8379 1.8716 1.8715 1.8715h19.461c0.4963-1.1e-4 0.9723-0.19737 1.3231-0.54839l7.8162-7.8161c0.7306-0.73081 0.7306-1.9154 0-2.6462l-5.0282-5.0282-2.3818 2.3818 3.9696 3.9696-6.3191 6.3191h-17.344v-26.946l17.321-0.0212 6.3429 6.3581-12.703 12.703-5.5574-5.5574 5.5574-5.5574 4.7635 4.7635 2.3818-2.3818-5.8217-5.8221c-0.7286-0.72842-1.9168-0.72974-2.6467 0l-7.6763 7.6763c-0.706 0.70636-0.733 1.8426-0.061 2.5817l7.7091 7.7091c0.7309 0.80387 1.9905 0.81846 2.7398 0.0317l14.796-14.864c0.7006-0.73553 0.6866-1.8956-0.032-2.614l-7.8253-7.8253c-0.351-0.35081-0.8269-0.54787-1.3231-0.54785z" fill="currentColor" fill-rule="evenodd"/><rect transform="matrix(.14035 0 0 .14035 1172 191.36)" x="-8.2421e-7" y="-1.0518e-16" width="256" height="256" fill="none"/></g></g>
                        </svg>
                        <p>Bonsai Integration disabled</p>
                        <p class="help-text">Please run the app from within Bonsai</p>
                    </div>
                {:else}
                    <div class="section">
                        <h3>Connection Status</h3>
                        <div class="connection-status {Bonsai.connected ? 'connected' : 'disconnected'}">
                            <div class="status-indicator"></div>
                            <span class="status-text">
                                {Bonsai.connected ? 'Connected' : 'Not Connected'}
                            </span>
                            {#if Bonsai.port}
                                <span class="status-details">Port: {Bonsai.port}</span>
                            {/if}
                        </div>
                        
                        <button class="load-btn" onclick={Bonsai.connected ? disconnect : connect}>
                            {#if Bonsai.connected}
                                <XIcon size={18} />
                            {:else}
                                <LinkIcon size={18} />
                            {/if}
                            {Bonsai.connected ? 'Disconnect' : 'Connect'}
                        </button>
                    </div>
                    
                    {#if Bonsai.connected}
                        <div class="section">
                            <button class="audit-btn" onclick={handleBonsaiAudit} disabled={Bonsai.auditing || !IDS.Module.activeDocument}>
                                {#if Bonsai.auditing}
                                    <svg class="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M21 12a9 9 0 11-6.219-8.56"/>
                                    </svg>
                                    Running Bonsai Audit...
                                {:else}
                                    <svg style="height: 18px; width: 18px;" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="32mm" height="32mm" version="1.1" viewBox="0 0 32 32" xml:space="preserve">
                                        <defs><linearGradient id="bonsai-audit-grad" x1="319.66" x2="414.22" y1="725.95" y2="631.1" gradientTransform="matrix(.34384 0 0 .34384 1065.6 -23.668)" gradientUnits="userSpaceOnUse"><stop stop-color="currentColor" offset="0" /><stop stop-color="currentColor" offset="1" /></linearGradient></defs>
                                        <g transform="translate(-1274.3 -68)"><g transform="matrix(.89066 0 0 .89066 230.47 -102.44)" clip-rule="evenodd"><path d="m1177.3 192.49c-1.0334-2e-5 -1.8713 0.83759-1.8715 1.871v29.941c0 1.0336 0.8379 1.8716 1.8715 1.8715h19.461c0.4963-1.1e-4 0.9723-0.19737 1.3231-0.54839l7.8162-7.8161c0.7306-0.73081 0.7306-1.9154 0-2.6462l-5.0282-5.0282-2.3818 2.3818 3.9696 3.9696-6.3191 6.3191h-17.344v-26.946l17.321-0.0212 6.3429 6.3581-12.703 12.703-5.5574-5.5574 5.5574-5.5574 4.7635 4.7635 2.3818-2.3818-5.8217-5.8221c-0.7286-0.72842-1.9168-0.72974-2.6467 0l-7.6763 7.6763c-0.706 0.70636-0.733 1.8426-0.061 2.5817l7.7091 7.7091c0.7309 0.80387 1.9905 0.81846 2.7398 0.0317l14.796-14.864c0.7006-0.73553 0.6866-1.8956-0.032-2.614l-7.8253-7.8253c-0.351-0.35081-0.8269-0.54787-1.3231-0.54785z" fill="currentColor" fill-rule="evenodd"/><rect transform="matrix(.14035 0 0 .14035 1172 191.36)" x="-8.2421e-7" y="-1.0518e-16" width="256" height="256" fill="none"/></g></g>
                                    </svg>
                                    Run Bonsai Audit
                                {/if}
                            </button>
                            {#if !IDS.Module.activeDocument}
                                <p class="help-text">Create or open an IDS document to enable auditing</p>
                            {/if}
                        </div>
                    {/if}
                {/if}
            {/if}
        </div>
    </div>
</div>

<style>
    .content-body {
        padding-top: 15px;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    
    .section {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .section h3 {
        margin: 0;
        font-size: 0.875rem;
        font-weight: 600;
        color: #acacac;
    }
    
    .load-btn, .audit-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        background: #ffffff12;
        color: white;
        border: none;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .load-btn:hover:not(:disabled), .audit-btn:hover:not(:disabled) {
        background: #ffffff1a;
    }
    
    .load-btn:disabled, .audit-btn:disabled {
        background: #ffffff0a;
        cursor: not-allowed;
    }
    
    .audit-btn {
        background: #12613d;
    }
    
    .audit-btn:hover:not(:disabled) {
        background: #197148;
    }
    
    .audit-btn:disabled {
        background: #ffffff24;
    }
    
    .spinner {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .models-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .model-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        border: 1px solid #e5e7eb24;
        border-radius: 0.375rem;
    }
    
    .model-info {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        width: calc(100% - 32px);
    }
    
    .model-name {
        font-size: 0.875rem;
        font-weight: 500;
        color: #ffffffd9;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        text-align: left;
    }
    
    .model-meta {
        display: flex;
        gap: 0.75rem;
        font-size: 0.75rem;
        color: #6b7280;
    }
    
    .unload-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 32px;
        height: 32px;
        background: none;
        color: #6b7280;
        border-radius: 0.25rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .unload-btn:hover {
        color: #ff7171;
    }
    
    .help-text {
        font-size: 0.75rem;
        color: #6b7280;
        margin: 0;
    }
    
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        text-align: center;
        color: #6b7280;
        flex: 1;
    }
    
    .empty-state svg {
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    .empty-state p {
        margin: 0.25rem 0;
    }
    
    .empty-state p:first-of-type {
        font-weight: 500;
        color: #8d8d8d;
    }
    
    .audit-reports {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .audit-report-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        border: 1px solid #e5e7eb24;
        border-radius: 0.375rem;
        cursor: pointer;
        transition: all 0.2s;
        background: none;
        color: inherit;
        text-align: left;
        width: 100%;
    }
    
    .audit-report-item:hover {
        background: #ffffff0a;
        border-color: #e5e7eb40;
    }
    
    .report-info {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        width: calc(100% - 32px);
    }
    
    .report-title {
        font-size: 0.875rem;
        font-weight: 500;
        color: #ffffffd9;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        text-align: left;
    }
    
    .report-meta {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.75rem;
    }
    
    .report-date {
        color: #6b7280;
    }
    
    .report-status {
        padding: 2px 6px;
        border-radius: 12px;
        font-size: 0.625rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .report-status.pass {
        border: 1px solid #30dea422;
        color: #10b981;
    }
    
    .report-status.fail {
        border: 1px solid #ff989863;
        color: #ff8282;
    }
    
    .report-summary {
        font-size: 0.75rem;
        color: #9ca3af;
    }
    
    .view-icon {
        color: #6b7280;
        margin-left: 0.5rem;
    }

    .report-progress {
        margin-top: 0.5rem;
        width: 100%;
    }

    .progress-bar-small {
        width: 100%;
        height: 4px;
        background: #ffffff12;
        border-radius: 2px;
        overflow: hidden;
    }

    .progress-fill-small {
        height: 100%;
        background: #ffffff4f;
        transition: width 0.3s ease;
        border-radius: 2px;
    }
    
    /* Minimization and Tab Styles */
    
    .content-header {
        display: flex;
        align-items: center;
    }
    
    .open-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 40px;
        background: none;
        color: #6b7280;
        border: none;
        border-radius: 0.25rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .open-btn:hover {
        color: #ffffffd9;
        background: #ffffff0a;
    }
    
    .tb-btn {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        background: none;
        color: #6b7280;
        border: none;
        border-radius: 0.375rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .tb-btn:hover {
        background: #ffffff12;
        color: #ffffffd9;
    }
    
    .tb-btn.active {
        background: #ffffff1a;
        color: #ffffffd9;
    }
    
    .tb-btn.active::after {
        content: '';
        position: absolute;
        right: -1px;
        top: 50%;
        transform: translateY(-50%);
        width: 1px;
        height: 24px;
        background: #12a05e;
        border-radius: 2px 0 0 2px;
    }
    
    /* Bonsai Integration Styles */
    .connection-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem;
        border: 1px solid #e5e7eb24;
        border-radius: 0.375rem;
        background: #ffffff06;
    }
    
    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #6b7280;
    }
    
    .connection-status.connected .status-indicator {
        background: #10b981;
        animation: pulse 2s infinite;
    }
    
    .connection-status.disconnected .status-indicator {
        background: #ef4444;
    }
    
    .status-text {
        font-size: 0.875rem;
        font-weight: 500;
        color: #ffffffd9;
    }
    
    .status-details {
        font-size: 0.75rem;
        color: #6b7280;
        margin-left: auto;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
</style>