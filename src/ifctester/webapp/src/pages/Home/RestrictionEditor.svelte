<script>
    import Svelecte from 'svelecte';
    import { getEntityClasses, getMaterialCategories, getClassificationSystems, getDataTypes, getPredefinedTypes, getEntityAttributes, getApplicablePsets } from '$src/modules/api/api.svelte.js';
    import * as IDS from '$src/modules/api/ids.svelte.js';
    
    let { facet = $bindable(), fieldName, label, placeholder, autocomplete = null, isSpecialProp = false } = $props();
    
    const isEntityNameField = autocomplete === 'entityName';
    const isMaterialField = autocomplete === 'material';
    const isClassificationSystemField = autocomplete === 'classificationSystem';
    const isPredefinedTypeField = autocomplete === 'predefinedType';
    const isAttributeNameField = autocomplete === 'attributeName';
    const isPropertySetField = autocomplete === 'propertySet';
    const isDataTypeField = autocomplete === 'dataType';
    
    // Predefined Types autocompletions
    let predefinedTypeOptions = $state([]);
    
    // Attribute Names autocompletions
    let attributeNameOptions = $state([]);
    
    // Property Sets autocompletions
    let propertySetOptions = $state([]);
    
    // Get the active specification's IFC schemas
    const getIfcVersions = () => {
        const activeDocument = IDS.Module.activeDocument ? IDS.Module.documents[IDS.Module.activeDocument] : null;
        const documentState = IDS.Module.activeDocument ? IDS.Module.states[IDS.Module.activeDocument] : null;
        const activeSpecification = activeDocument && documentState?.activeSpecification !== null && activeDocument.specifications?.specification ? 
            activeDocument.specifications.specification[documentState.activeSpecification] : null;
        
        const versions = activeSpecification?.["@ifcVersion"] || ['IFC4'];
        // TODO: Fix: Filter out IFC4X3 because it's buggy
        return versions.filter(version => version !== 'IFC4X3_ADD2');
    };
    
    // Get the entity name from facet
    const getEntityName = () => {
        const nameField = facet?.name;
        if (!nameField) return '';
        if (nameField.simpleValue) return nameField.simpleValue;
        return '';
    };
    
    // Get all entity names from Entity facets in Applicability
    const getApplicabilityEntityNames = () => {
        const activeDocument = IDS.Module.activeDocument ? IDS.Module.documents[IDS.Module.activeDocument] : null;
        const documentState = IDS.Module.activeDocument ? IDS.Module.states[IDS.Module.activeDocument] : null;
        const activeSpecification = activeDocument && documentState?.activeSpecification !== null && activeDocument.specifications?.specification ? 
            activeDocument.specifications.specification[documentState.activeSpecification] : null;
        
        if (!activeSpecification?.applicability?.entity) return [];
        
        const entityFacets = activeSpecification.applicability.entity;
        const entityNames = [];
        
        entityFacets.forEach(entityFacet => {
            const nameField = entityFacet.name;
            if (!nameField) return;
            
            if (nameField.simpleValue) {
                entityNames.push(nameField.simpleValue);
            } else if (nameField.restriction?.enumeration) {
                nameField.restriction.enumeration.forEach(enumItem => {
                    if (enumItem['@value']) {
                        entityNames.push(enumItem['@value']);
                    }
                });
            }
        });
        
        return [...new Set(entityNames)]; // Deduplicate
    };
    
    // Get entity facets with their predefined types
    const getApplicabilityEntityFacets = () => {
        const activeDocument = IDS.Module.activeDocument ? IDS.Module.documents[IDS.Module.activeDocument] : null;
        const documentState = IDS.Module.activeDocument ? IDS.Module.states[IDS.Module.activeDocument] : null;
        const activeSpecification = activeDocument && documentState?.activeSpecification !== null && activeDocument.specifications?.specification ? 
            activeDocument.specifications.specification[documentState.activeSpecification] : null;
        
        if (!activeSpecification?.applicability?.entity) return [];
        
        return activeSpecification.applicability.entity.map(entityFacet => {
            const nameField = entityFacet.name;
            const predefinedTypeField = entityFacet.predefinedType;
            
            // Extract entity name
            let entityNames = [];
            if (nameField?.simpleValue) {
                entityNames = [nameField.simpleValue];
            } else if (nameField?.restriction?.enumeration) {
                entityNames = nameField.restriction.enumeration
                    .map(item => item['@value'])
                    .filter(Boolean);
            }
            
            // Extract predefined type
            let predefinedType = '';
            if (predefinedTypeField?.simpleValue) {
                predefinedType = predefinedTypeField.simpleValue;
            } else if (predefinedTypeField?.restriction?.enumeration?.length > 0) {
                // For enumeration predefined types, use the first one or empty string
                predefinedType = predefinedTypeField.restriction.enumeration[0]['@value'] || '';
            }
            
            return { entityNames, predefinedType };
        }).filter(facet => facet.entityNames.length > 0);
    };
    
    // Contextual autocompletions
    $effect(async () => {

        // Predefined Types
        if (isPredefinedTypeField) {
            const entityName = getEntityName();
            const ifcVersions = getIfcVersions();
            
            if (entityName && entityName.trim() !== '' && ifcVersions.length > 0) {
                try {
                    // Fetch predefined types for all selected schemas
                    const typePromises = ifcVersions.map(schema => 
                        getPredefinedTypes(schema, entityName.toUpperCase())
                    );
                    const typeSets = await Promise.all(typePromises);
                    
                    // Deduplicate predefined types across all schemas
                    const allTypes = new Set();
                    typeSets.forEach(types => {
                        if (types && Array.isArray(types)) {
                            types.forEach(type => allTypes.add(type));
                        }
                    });
                    
                    predefinedTypeOptions = Array.from(allTypes).sort();
                } catch (error) {
                    console.error('Failed to fetch predefined types:', error);
                    predefinedTypeOptions = [];
                }
            } else {
                predefinedTypeOptions = [];
            }
        }
        
        // Attribute Names
        if (isAttributeNameField) {
            const entityNames = getApplicabilityEntityNames();
            const ifcVersions = getIfcVersions();
            
            if (entityNames.length > 0 && ifcVersions.length > 0) {
                try {
                    // Fetch attributes for all entity names across all selected schemas
                    const attributePromises = [];
                    entityNames.forEach(entityName => {
                        ifcVersions.forEach(schema => {
                            attributePromises.push(
                                getEntityAttributes(schema, entityName.toUpperCase())
                            );
                        });
                    });
                    
                    const attributeSets = await Promise.all(attributePromises);
                    
                    // Deduplicate attribute names across all entities and schemas
                    const allAttributes = new Set();
                    attributeSets.forEach(attributes => {
                        if (attributes && Array.isArray(attributes)) {
                            attributes.forEach(attr => {
                                if (attr.name) {
                                    allAttributes.add(attr.name);
                                }
                            });
                        }
                    });
                    
                    attributeNameOptions = Array.from(allAttributes).sort();
                } catch (error) {
                    console.error('Failed to fetch attribute names:', error);
                    attributeNameOptions = [];
                }
            } else {
                attributeNameOptions = [];
            }
        }
        
        // Property Sets
        if (isPropertySetField) {
            const entityFacets = getApplicabilityEntityFacets();
            const ifcVersions = ['IFC4']; // TODO: Fix this. Even IFC2X3 doesn't work and throws an error.
            
            if (entityFacets.length > 0 && ifcVersions.length > 0) {
                try {
                    // Fetch applicable property sets for all entity facets across all selected schemas
                    const psetPromises = [];
                    entityFacets.forEach(facet => {
                        facet.entityNames.forEach(entityName => {
                            ifcVersions.forEach(schema => {
                                psetPromises.push(
                                    getApplicablePsets(schema, entityName.toUpperCase(), facet.predefinedType)
                                );
                            });
                        });
                    });
                    
                    const psetSets = await Promise.all(psetPromises);
                    
                    // Deduplicate property set names
                    const allPsets = new Set();
                    psetSets.forEach(psets => {
                        if (psets && Array.isArray(psets)) {
                            psets.forEach(pset => allPsets.add(pset));
                        }
                    });
                    
                    propertySetOptions = Array.from(allPsets).sort();
                } catch (error) {
                    console.error('Failed to fetch property sets:', error);
                    propertySetOptions = [];
                }
            } else {
                propertySetOptions = [];
            }
        }
    });
    
    // Get autocomplete options based on field type
    const getAutocompleteOptions = () => {
        if (isEntityNameField) return getEntityClasses();
        if (isMaterialField) return getMaterialCategories();
        if (isClassificationSystemField) return Object.keys(getClassificationSystems());
        if (isPredefinedTypeField) return predefinedTypeOptions;
        if (isAttributeNameField) return attributeNameOptions;
        if (isPropertySetField) return propertySetOptions;
        if (isDataTypeField) return getDataTypes();
        return [];
    };
    
    const getRestrictionType = () => {
        const fieldValue = facet[fieldName];
        if (!fieldValue) return 'Simple';
        if (fieldValue.simpleValue !== undefined) return 'Simple';
        if (fieldValue['restriction']) {
            const restriction = fieldValue['restriction'];
            if (restriction['enumeration']) return 'Enumeration';
            if (restriction['pattern']) return 'Pattern';
            if (restriction['minInclusive'] || restriction['maxInclusive'] || 
                restriction['minExclusive'] || restriction['maxExclusive']) return 'Range';
            if (restriction['length']) return 'Length';
            if (restriction['minLength'] || restriction['maxLength']) return 'Length Range';
        }
        return 'Simple';
    };
    
    const getSimpleValue = () => {
        const fieldValue = facet[fieldName];

        // For special properties (eg. @dataType), we return the value directly
        if (isSpecialProp) return fieldValue || null;

        if (!fieldValue) return null;
        if (fieldValue.simpleValue !== undefined) return fieldValue.simpleValue;
        return null;
    };

    const getEnumerationValues = () => {
        const fieldValue = facet[fieldName];
        if (!fieldValue?.['restriction']) return [''];
        const restriction = fieldValue['restriction'];
        const enumValues = restriction['enumeration'];
        if (!enumValues) return [''];
        return enumValues.map(item => item['@value'] || '');
    };

    const getPatternValue = () => {
        const fieldValue = facet[fieldName];
        if (!fieldValue?.['restriction']) return '';
        const restriction = fieldValue['restriction'];
        const pattern = restriction['pattern'];
        if (!pattern || !pattern.length) return '';
        return pattern[0]['@value'] || '';
    };

    const getRangeValues = () => {
        const fieldValue = facet[fieldName];
        if (!fieldValue?.['restriction']) return { min: '', max: '', minType: 'Inclusive', maxType: 'Inclusive' };
        const restriction = fieldValue['restriction'];
        
        let min = '', max = '', minType = 'Inclusive', maxType = 'Inclusive';
        
        if (restriction['minInclusive']?.length) {
            min = restriction['minInclusive'][0]['@value'] || '';
            minType = 'Inclusive';
        } else if (restriction['minExclusive']?.length) {
            min = restriction['minExclusive'][0]['@value'] || '';
            minType = 'Exclusive';
        }
        
        if (restriction['maxInclusive']?.length) {
            max = restriction['maxInclusive'][0]['@value'] || '';
            maxType = 'Inclusive';
        } else if (restriction['maxExclusive']?.length) {
            max = restriction['maxExclusive'][0]['@value'] || '';
            maxType = 'Exclusive';
        }
        
        return { min, max, minType, maxType };
    };

    const getLengthValue = () => {
        const fieldValue = facet[fieldName];
        if (!fieldValue?.['restriction']) return '';
        const restriction = fieldValue['restriction'];
        const length = restriction['length'];
        if (!length || !length.length) return '';
        return length[0]['@value'] || '';
    };

    const getLengthRangeValues = () => {
        const fieldValue = facet[fieldName];
        if (!fieldValue?.['restriction']) return { min: '', max: '' };
        const restriction = fieldValue['restriction'];
        
        let min = '', max = '';
        
        if (restriction['minLength']?.length) {
            min = restriction['minLength'][0]['@value'] || '';
        }
        if (restriction['maxLength']?.length) {
            max = restriction['maxLength'][0]['@value'] || '';
        }
        
        return { min, max };
    };

    const setSimpleValue = (value) => {
        // For special properties (eg. @dataType), we set the value directly
        if (isSpecialProp) {
            facet[fieldName] = value;
            return;
        }
        if (!facet[fieldName]) facet[fieldName] = {};
        facet[fieldName] = { simpleValue: value };
    };

    const setEnumerationValues = (values) => {
        if (!facet[fieldName]) facet[fieldName] = {};
        const enumItems = values.filter(v => v && typeof v === 'string' && v.trim() !== '').map(v => ({ '@value': v }));
        facet[fieldName] = {
            'restriction': {
                '@base': 'xs:string',
                'enumeration': enumItems
            }
        };
    };

    const setPatternValue = (value) => {
        if (!facet[fieldName]) facet[fieldName] = {};
        facet[fieldName] = {
            'restriction': {
                '@base': 'xs:string',
                'pattern': [{ '@value': value }]
            }
        };
    };

    const setRangeValues = (min, max, minType, maxType) => {
        if (!facet[fieldName]) facet[fieldName] = {};
        const restriction = { '@base': 'xs:string' };
        
        if (min !== '') {
            const minKey = minType === 'Inclusive' ? 'minInclusive' : 'minExclusive';
            restriction[minKey] = [{ '@value': min }];
        }
        if (max !== '') {
            const maxKey = maxType === 'Inclusive' ? 'maxInclusive' : 'maxExclusive';
            restriction[maxKey] = [{ '@value': max }];
        }
        
        facet[fieldName] = { 'restriction': restriction };
    };

    const setLengthValue = (value) => {
        if (!facet[fieldName]) facet[fieldName] = {};
        facet[fieldName] = {
            'restriction': {
                '@base': 'xs:string',
                'length': [{ '@value': value }]
            }
        };
    };

    const setLengthRangeValues = (min, max) => {
        if (!facet[fieldName]) facet[fieldName] = {};
        const restriction = { '@base': 'xs:string' };
        
        if (min !== '') restriction['minLength'] = [{ '@value': min }];
        if (max !== '') restriction['maxLength'] = [{ '@value': max }];
        
        facet[fieldName] = { 'restriction': restriction };
    };

    let restrictionType = $derived(getRestrictionType());
    let enumerationValues = $derived(getEnumerationValues());

    const handleTypeChange = (newType) => {
        restrictionType = newType;
        
        switch (newType) {
            case 'Simple':
                setSimpleValue(getSimpleValue() || '');
                break;
            case 'Enumeration':
                const currentEnumValues = getEnumerationValues();
                enumerationValues = currentEnumValues.length > 0 ? currentEnumValues : [''];
                setEnumerationValues(enumerationValues);
                break;
            case 'Pattern':
                setPatternValue(getPatternValue() || '');
                break;
            case 'Range':
                const range = getRangeValues();
                setRangeValues(range.min, range.max, range.minType, range.maxType);
                break;
            case 'Length':
                setLengthValue(getLengthValue() || '');
                break;
            case 'Length Range':
                const lengthRange = getLengthRangeValues();
                setLengthRangeValues(lengthRange.min, lengthRange.max);
                break;
        }
    };

    const addEnumerationValue = () => {
        enumerationValues = [...enumerationValues, ''];
    };

    const removeEnumerationValue = (index) => {
        enumerationValues = enumerationValues.filter((_, i) => i !== index);
        setEnumerationValues(enumerationValues);
    };

    const updateEnumerationValue = (index, value) => {
        enumerationValues[index] = value;
        setEnumerationValues(enumerationValues);
    };
</script>

<div class="form-group">
    <label>{label}</label>
    <div class="restriction-controls">
        {#if !isSpecialProp}
            <div class="restriction-type-selector">
                <select class="form-input" bind:value={restrictionType} onchange={(e) => handleTypeChange(e.target.value)}>
                    <option value="Simple">Simple</option>
                    <option value="Enumeration">Enumeration</option>
                    <option value="Pattern">Pattern</option>
                    <option value="Range">Range</option>
                    <option value="Length">Length</option>
                    <option value="Length Range">Length Range</option>
                </select>
            </div>
        {/if}
        
        <div class="restriction-content">
            {#if restrictionType === 'Simple'}
                {#if autocomplete}
                    <Svelecte 
                        class="form-ac-input" 
                        options={getAutocompleteOptions()} 
                        allowEditing={true} 
                        creatable={true} 
                        creatablePrefix="" 
                        strictMode={false}
                        resetOnBlur={false} 
                        bind:value={() => getSimpleValue(), (v) => setSimpleValue(v)} 
                        placeholder={placeholder}
                    />
                {:else}
                    <input class="form-input" type="text" bind:value={() => getSimpleValue(), (v) => setSimpleValue(v)} {placeholder}>
                {/if}
            
            {:else if restrictionType === 'Enumeration'}
                <div class="enumeration-list">
                    {#each enumerationValues as value, index}
                        <div class="enumeration-item">
                            {#if autocomplete}
                                <Svelecte 
                                    class="form-ac-input" 
                                    options={getAutocompleteOptions()} 
                                    allowEditing={true} 
                                    creatable={true} 
                                    creatablePrefix="" 
                                    strictMode={false}
                                    resetOnBlur={false} 
                                    bind:value={() => value, (v) => updateEnumerationValue(index, v)} 
                                    placeholder={placeholder} 
                                />
                            {:else}
                                <input class="form-input" type="text" value={value} oninput={(e) => updateEnumerationValue(index, e.target.value)} {placeholder}>
                            {/if}
                            <button class="btn-delete" onclick={() => removeEnumerationValue(index)} type="button" aria-label="Remove enumeration value">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M18 6L6 18M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>
                    {/each}
                    <button class="btn-add" onclick={addEnumerationValue} type="button" aria-label="Add enumeration value">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                    </button>
                </div>
            
            {:else if restrictionType === 'Pattern'}
                <input class="form-input" type="text" bind:value={() => getPatternValue(), (v) => setPatternValue(v)} placeholder="Enter regex pattern (e.g., DT[0-9]{2})">
            
            {:else if restrictionType === 'Range'}
                <div class="range-controls">
                    <div class="range-group">
                        <label>Min</label>
                        <input class="form-input" type="text" bind:value={() => getRangeValues().min, (v) => { const range = getRangeValues(); setRangeValues(v, range.max, range.minType, range.maxType); }} placeholder="0">
                        <select class="form-input" bind:value={() => getRangeValues().minType, (v) => { const range = getRangeValues(); setRangeValues(range.min, range.max, v, range.maxType); }}>
                            <option value="Inclusive">Inclusive</option>
                            <option value="Exclusive">Exclusive</option>
                        </select>
                    </div>
                    <div class="range-group">
                        <label>Max</label>
                        <input class="form-input" type="text" bind:value={() => getRangeValues().max, (v) => { const range = getRangeValues(); setRangeValues(range.min, v, range.minType, range.maxType); }} placeholder="0">
                        <select class="form-input" bind:value={() => getRangeValues().maxType, (v) => { const range = getRangeValues(); setRangeValues(range.min, range.max, range.minType, v); }}>
                            <option value="Inclusive">Inclusive</option>
                            <option value="Exclusive">Exclusive</option>
                        </select>
                    </div>
                </div>
            
            {:else if restrictionType === 'Length'}
                <input class="form-input" type="number" bind:value={() => getLengthValue(), (v) => setLengthValue(v)} placeholder="Enter exact length">
            
            {:else if restrictionType === 'Length Range'}
                <div class="length-range-controls">
                    <div class="length-group">
                        <label>Min Length</label>
                        <input class="form-input" type="number" bind:value={() => getLengthRangeValues().min, (v) => { const range = getLengthRangeValues(); setLengthRangeValues(v, range.max); }} placeholder="0">
                    </div>
                    <div class="length-group">
                        <label>Max Length</label>
                        <input class="form-input" type="number" bind:value={() => getLengthRangeValues().max, (v) => { const range = getLengthRangeValues(); setLengthRangeValues(range.min, v); }} placeholder="0">
                    </div>
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    .restriction-controls {
        display: flex;
        gap: 10px;
        align-items: flex-start;
    }

    .restriction-type-selector {
        min-width: 140px;
    }

    .restriction-content {
        flex: 1;
    }

    .enumeration-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .enumeration-item {
        display: flex;
        gap: 8px;
        align-items: center;
    }

    .enumeration-item .form-input,
    .enumeration-item :global(.form-ac-input) {
        flex: 1;
    }

    .btn-delete, .btn-add {
        background: none;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 8px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .btn-delete {
        color: #b0b0b0;
        border-color: #ffffff26;
        border-radius: 50px;
        padding: 5px;
    }

    .btn-delete:hover {
        background: #ffffff12;
        color: white;
    }

    .btn-add {
        color: #007bff;
        border-color: #007bff;
        align-self: flex-start;
    }

    .btn-add:hover {
        background: #007bff;
        color: white;
    }

    .range-controls {
        display: flex;
        gap: 20px;
        align-items: flex-end;
    }

    .range-group {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .range-group label {
        font-size: 12px;
        color: #666;
        margin: 0;
    }

    .length-range-controls {
        display: flex;
        gap: 20px;
        align-items: flex-end;
    }

    .length-group {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .length-group label {
        font-size: 12px;
        color: #666;
        margin: 0;
    }
</style>