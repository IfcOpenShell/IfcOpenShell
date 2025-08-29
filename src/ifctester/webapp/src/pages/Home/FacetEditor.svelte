<script>
    import RestrictionEditor from './RestrictionEditor.svelte';
    import {stringifyFacet} from "$src/modules/api/ids.svelte.js";
    
    /**
     * Applicability facets wont have: "@uri", "@instructions", "@cardinality"
     * @ in name --> simple string value
     * else --> can be simpleValue, Restriction or list of Restrictions
    */
    let { facet = $bindable(), facetType, activeTab, removeFacet, index, specification } = $props();

    const getSpecialProp = (prop) => {
        return facet[prop] ?? "";
    };
    const setSpecialProp = (prop, value) => {
        facet[prop] = value;
    };
</script>

<div class="restriction-item">
    <div class="restriction-header">
        <span class="restriction-type">{facetType.toUpperCase()}</span>
        <span class="restriction-name">{@html stringifyFacet(activeTab, facet, facetType, specification)}</span>
        <button class="btn-delete" onclick={() => removeFacet(facetType, index)} aria-label="Delete Restriction">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"></path>
            </svg>
        </button>
    </div>
    <div class="restriction-form">
        {#if facetType === 'entity'}
            <RestrictionEditor bind:facet={facet} fieldName="name" label="Entity Name" placeholder="e.g., IfcWall" autocomplete="entityName" />
            <RestrictionEditor bind:facet={facet} fieldName="predefinedType" label="Predefined Type" placeholder="e.g., SOLIDWALL" autocomplete="predefinedType" />
        {:else if facetType === 'attribute'}
            <RestrictionEditor bind:facet={facet} fieldName="name" label="Attribute Name" placeholder="e.g., Name" autocomplete="attributeName" />
            <RestrictionEditor bind:facet={facet} fieldName="value" label="Value" placeholder="Optional value" />
        {:else if facetType === 'property'}
            <RestrictionEditor bind:facet={facet} fieldName="propertySet" label="Property Set" placeholder="e.g., Pset_WallCommon" autocomplete="propertySet" />
            <RestrictionEditor bind:facet={facet} fieldName="baseName" label="Base Name" placeholder="e.g., FireRating" />
            <RestrictionEditor bind:facet={facet} fieldName="value" label="Value" placeholder="Optional value" />
            <RestrictionEditor bind:facet={facet} fieldName="@dataType" label="Data Type" placeholder="Optional data type" autocomplete="dataType" isSpecialProp={true} />
        {:else if facetType === 'material'}
            <RestrictionEditor bind:facet={facet} fieldName="value" label="Material Value" placeholder="e.g., Concrete" autocomplete="material" />
        {:else if facetType === 'classification'}
            <RestrictionEditor bind:facet={facet} fieldName="system" label="System" placeholder="e.g., Uniclass 2015" autocomplete="classificationSystem" />
            <RestrictionEditor bind:facet={facet} fieldName="value" label="Value" placeholder="e.g., EF_25_10_25" />
        {:else if facetType === 'partOf'}
            <RestrictionEditor bind:facet={facet} fieldName="name" label="Entity Name" placeholder="e.g., IfcSpace" autocomplete="entityName" />
            <RestrictionEditor bind:facet={facet} fieldName="predefinedType" label="Predefined Type" placeholder="e.g., SOLIDWALL" autocomplete="predefinedType" />
            <div class="form-group">
                <label>Relation</label>
                <select class="form-input" bind:value={() => getSpecialProp("@relation"), (v) => setSpecialProp("@relation", v)}>
                    <option value="">Select relation...</option>
                    <option value="IFCRELAGGREGATES">IFCRELAGGREGATES</option>
                    <option value="IFCRELASSIGNSTOGROUP">IFCRELASSIGNSTOGROUP</option>
                    <option value="IFCRELCONTAINEDINSPATIALSTRUCTURE">IFCRELCONTAINEDINSPATIALSTRUCTURE</option>
                    <option value="IFCRELNESTS">IFCRELNESTS</option>
                    <option value="IFCRELVOIDSELEMENT IFCRELFILLSELEMENT">IFCRELVOIDSELEMENT IFCRELFILLSELEMENT</option>
                </select>
            </div>
        {/if}
        {#if activeTab === 'requirements'}
            {#if facetType !== 'entity'}
                <div class="form-group">
                    <label>Cardinality</label>
                    <select class="form-input" bind:value={() => getSpecialProp("@cardinality"), (v) => setSpecialProp("@cardinality", v)}>
                        <option value="required">Required</option>
                        <option value="optional">Optional</option>
                        <option value="prohibited">Prohibited</option>
                    </select>
                </div>
            {/if}
            <div class="form-group full-width">
                <label>Instructions</label>
                <textarea class="form-input" bind:value={() => getSpecialProp("@instructions"), (v) => setSpecialProp("@instructions", v)} placeholder="Optional instructions for IFC authors" rows="2"></textarea>
            </div>
        {/if}
    </div>
</div>