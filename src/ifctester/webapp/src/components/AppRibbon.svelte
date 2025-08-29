<script>
    import { onMount } from "svelte";
    import { Module } from "$src/modules/api/ids.svelte.js";
</script>

<div class="app-ribbon">
    {#if Module.status === 'loading'}
        <div class="status-indicator">
            <div class="spinner"></div>
            <span>Loading IfcOpenShell...</span>
        </div>
    {:else if Module.status === 'ready'}
        <div class="status-indicator ready">
            <div class="status-dot"></div>
            <span>Ready</span>
        </div>
    {:else if Module.status === 'error'}
        <div class="status-indicator error">
            <div class="error-dot"></div>
            <span>Error</span>
        </div>
    {/if}
</div>