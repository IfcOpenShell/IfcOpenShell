<script>
    import * as IDS from "$src/modules/api/ids.svelte.js";
    
    let activeDocument = $derived(IDS.Module.activeDocument ? IDS.Module.documents[IDS.Module.activeDocument] : null);

    const getProp = (prop) => {
        return activeDocument?.info[prop] ?? "";
    };
    
    const setProp = (prop, value) => {
        activeDocument.info[prop] = value;
    };
</script>

<div class="ids-info">
    <div class="ids-md-header">
        <h2>IDS Information</h2>
    </div>
    <div class="form-grid">
        <div class="form-group">
            <label>Title</label>
            <input class="form-input" type="text" bind:value={() => getProp("title"), (v) => setProp("title", v)} placeholder="Enter IDS title">
        </div>
        <div class="form-group">
            <label>Author Email</label>
            <input class="form-input" type="email" bind:value={() => getProp("author"), (v) => setProp("author", v)} placeholder="Enter author">
        </div>
        <div class="form-group">
            <label>Version</label>
            <input class="form-input" type="text" bind:value={() => getProp("version"), (v) => setProp("version", v)} placeholder="Enter version">
        </div>
        <div class="form-group">
            <label>Date</label>
            <input class="form-input" type="date" bind:value={() => getProp("date"), (v) => setProp("date", v)}>
        </div>
        <div class="form-group full-width">
            <label>Description</label>
            <textarea class="form-input" bind:value={() => getProp("description"), (v) => setProp("description", v)} placeholder="Enter description" rows="3"></textarea>
        </div>
        <div class="form-group">
            <label>Purpose</label>
            <input class="form-input" type="text" bind:value={() => getProp("purpose"), (v) => setProp("purpose", v)} placeholder="Enter purpose">
        </div>
        <div class="form-group">
            <label>Milestone</label>
            <input class="form-input" type="text" bind:value={() => getProp("milestone"), (v) => setProp("milestone", v)} placeholder="Enter milestone">
        </div>
        <div class="form-group full-width">
            <label>Copyright</label>
            <input class="form-input" type="text" bind:value={() => getProp("copyright"), (v) => setProp("copyright", v)} placeholder="Enter copyright">
        </div>
    </div>
</div>
