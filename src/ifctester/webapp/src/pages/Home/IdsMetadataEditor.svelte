<script lang="ts">
    import * as IDS from "$src/modules/api/ids.svelte";
    import type { IdsDocument, IdsInfo } from "$src/types/ids";
    
    let activeDocument = $derived(
        IDS.Module.activeDocument ? (IDS.Module.documents[IDS.Module.activeDocument] as IdsDocument) : null
    );

    const getProp = (prop: keyof IdsInfo) => {
        return activeDocument?.info[prop] ?? "";
    };
    
    const setProp = (prop: keyof IdsInfo, value: string) => {
        if (!activeDocument) return;
        activeDocument.info[prop] = value;
    };
</script>

<div class="ids-info">
    <div class="ids-md-header">
        <h2>IDS Information</h2>
    </div>
    <div class="form-grid">
        <div class="form-group">
            <label for="ids-title">Title</label>
            <input class="form-input" id="ids-title" type="text" bind:value={() => getProp("title"), (v) => setProp("title", v)} placeholder="Enter IDS title">
        </div>
        <div class="form-group">
            <label for="ids-author">Author Email</label>
            <input class="form-input" id="ids-author" type="email" bind:value={() => getProp("author"), (v) => setProp("author", v)} placeholder="Enter author">
        </div>
        <div class="form-group">
            <label for="ids-version">Version</label>
            <input class="form-input" id="ids-version" type="text" bind:value={() => getProp("version"), (v) => setProp("version", v)} placeholder="Enter version">
        </div>
        <div class="form-group">
            <label for="ids-date">Date</label>
            <input class="form-input" id="ids-date" type="date" bind:value={() => getProp("date"), (v) => setProp("date", v)}>
        </div>
        <div class="form-group full-width">
            <label for="ids-description">Description</label>
            <textarea class="form-input" id="ids-description" bind:value={() => getProp("description"), (v) => setProp("description", v)} placeholder="Enter description" rows="3"></textarea>
        </div>
        <div class="form-group">
            <label for="ids-purpose">Purpose</label>
            <input class="form-input" id="ids-purpose" type="text" bind:value={() => getProp("purpose"), (v) => setProp("purpose", v)} placeholder="Enter purpose">
        </div>
        <div class="form-group">
            <label for="ids-milestone">Milestone</label>
            <input class="form-input" id="ids-milestone" type="text" bind:value={() => getProp("milestone"), (v) => setProp("milestone", v)} placeholder="Enter milestone">
        </div>
        <div class="form-group full-width">
            <label for="ids-copyright">Copyright</label>
            <input class="form-input" id="ids-copyright" type="text" bind:value={() => getProp("copyright"), (v) => setProp("copyright", v)} placeholder="Enter copyright">
        </div>
    </div>
</div>
