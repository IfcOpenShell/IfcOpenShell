<script lang="ts">
    import Svelecte from 'svelecte';
    import {
        getApplicablePsets,
        getClassificationSystems,
        getDataTypes,
        getEntityAttributes,
        getEntityClasses,
        getMaterialCategories,
        getPredefinedTypes
    } from '$src/modules/api/api.svelte';
    import * as IDS from '$src/modules/api/ids.svelte';
    import type { DocumentState, Facet, FacetValue, IdsDocument, Restriction, RestrictionValue, Specification } from '$src/types/ids';
    
    type AutocompleteType =
        | 'entityName'
        | 'material'
        | 'classificationSystem'
        | 'predefinedType'
        | 'attributeName'
        | 'propertySet'
        | 'dataType'
        | null;

    let {
        facet = $bindable<Facet>({}),
        fieldName,
        label,
        placeholder,
        autocomplete = null,
        isSpecialProp = false
    }: {
        facet: Facet;
        fieldName: string;
        label: string;
        placeholder: string;
        autocomplete?: AutocompleteType;
        isSpecialProp?: boolean;
    } = $props();

    let isEntityNameField = $derived(autocomplete === 'entityName');
    let isMaterialField = $derived(autocomplete === 'material');
    let isClassificationSystemField = $derived(autocomplete === 'classificationSystem');
    let isPredefinedTypeField = $derived(autocomplete === 'predefinedType');
    let isAttributeNameField = $derived(autocomplete === 'attributeName');
    let isPropertySetField = $derived(autocomplete === 'propertySet');
    let isDataTypeField = $derived(autocomplete === 'dataType');

    const uniqueId = Math.random().toString(36).slice(2, 8);
    let baseId = $derived(`restriction-${fieldName}-${uniqueId}`);

    const activeDocument = $derived(
        IDS.Module.activeDocument ? (IDS.Module.documents[IDS.Module.activeDocument] as IdsDocument) : null
    );
    const documentState = $derived(
        IDS.Module.activeDocument ? (IDS.Module.states[IDS.Module.activeDocument] as DocumentState) : null
    );
    const activeSpecification = $derived(
        activeDocument && documentState && documentState.activeSpecification !== null && activeDocument.specifications?.specification
            ? (activeDocument.specifications.specification[documentState.activeSpecification] as Specification)
            : null
    );

    const getFieldValue = () => (facet as Record<string, unknown>)[fieldName] as FacetValue | string | undefined;
    const setFieldValue = (value: FacetValue | string) => {
        (facet as Record<string, unknown>)[fieldName] = value;
    };
    const getFacetValue = () => {
        const value = getFieldValue();
        return typeof value === 'object' && value !== null ? (value as FacetValue) : undefined;
    };
    
    // Predefined Types autocompletions
    let predefinedTypeOptions: string[] = $state([]);
    
    // Attribute Names autocompletions
    let attributeNameOptions: string[] = $state([]);
    
    // Property Sets autocompletions
    let propertySetOptions: string[] = $state([]);
    
    // Get the active specification's IFC schemas
    const getIfcVersions = () => {
        const versions = activeSpecification?.["@ifcVersion"] || ['IFC4'];
        // TODO: Fix: Filter out IFC4X3 because it's buggy
        return versions.filter(version => version !== 'IFC4X3_ADD2');
    };
    
    // Get the entity name from facet
    const getEntityName = () => {
        const nameField = (facet as Record<string, unknown>)?.name as FacetValue | undefined;
        if (!nameField) return '';
        if (nameField.simpleValue) return nameField.simpleValue;
        return '';
    };
    
    // Get all entity names from Entity facets in Applicability
    const getApplicabilityEntityNames = () => {
        if (!activeSpecification?.applicability?.entity) return [];
        
        const entityFacets = activeSpecification.applicability.entity as Facet[];
        const entityNames: string[] = [];
        
        entityFacets.forEach(entityFacet => {
            const nameField = (entityFacet as Record<string, unknown>).name as FacetValue | undefined;
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
        if (!activeSpecification?.applicability?.entity) return [];
        
        return (activeSpecification.applicability.entity as Facet[]).map(entityFacet => {
            const nameField = (entityFacet as Record<string, unknown>).name as FacetValue | undefined;
            const predefinedTypeField = (entityFacet as Record<string, unknown>).predefinedType as FacetValue | undefined;
            
            // Extract entity name
            let entityNames: string[] = [];
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
            } else {
                const enumValues = predefinedTypeField?.restriction?.enumeration;
                if (enumValues && enumValues.length > 0) {
                    // For enumeration predefined types, use the first one or empty string
                    predefinedType = enumValues[0]['@value'] || '';
                }
            }
            
            return { entityNames, predefinedType };
        }).filter(facet => facet.entityNames.length > 0);
    };
    
    // Contextual autocompletions
    $effect(() => {
        void (async () => {

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
                    const typeSets = await Promise.all(typePromises) as string[][];
                    
                    // Deduplicate predefined types across all schemas
                    const allTypes = new Set<string>();
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
                    const attributePromises: Array<Promise<{ name: string }[]>> = [];
                    entityNames.forEach(entityName => {
                        ifcVersions.forEach(schema => {
                            attributePromises.push(
                                getEntityAttributes(schema, entityName.toUpperCase()) as Promise<{ name: string }[]>
                            );
                        });
                    });
                    
                    const attributeSets = await Promise.all(attributePromises) as { name: string }[][];
                    
                    // Deduplicate attribute names across all entities and schemas
                    const allAttributes = new Set<string>();
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
                    const psetPromises: Array<Promise<string[]>> = [];
                    entityFacets.forEach(facet => {
                        facet.entityNames.forEach(entityName => {
                            ifcVersions.forEach(schema => {
                                psetPromises.push(
                                    getApplicablePsets(schema, entityName.toUpperCase(), facet.predefinedType) as Promise<string[]>
                                );
                            });
                        });
                    });
                    
                    const psetSets = await Promise.all(psetPromises) as string[][];
                    
                    // Deduplicate property set names
                    const allPsets = new Set<string>();
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
        })();
    });
    
    // Get autocomplete options based on field type
    const getAutocompleteOptions = (): string[] => {
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
        const fieldValue = getFacetValue();
        if (!fieldValue) return 'Simple';
        if (fieldValue.simpleValue !== undefined) return 'Simple';
        if (fieldValue['restriction']) {
            const restriction = fieldValue['restriction'] as Restriction;
            if (restriction['enumeration']) return 'Enumeration';
            if (restriction['pattern']) return 'Pattern';
            if (restriction['minInclusive'] || restriction['maxInclusive'] || 
                restriction['minExclusive'] || restriction['maxExclusive']) return 'Range';
            if (restriction['length']) return 'Length';
            if (restriction['minLength'] || restriction['maxLength']) return 'Length Range';
        }
        return 'Simple';
    };
    
    const getSimpleValue = (): string => {
        const fieldValue = getFieldValue();

        // For special properties (eg. @dataType), we return the value directly
        if (typeof fieldValue === 'string') return fieldValue;
        if (isSpecialProp) return '';

        if (!fieldValue) return '';
        if (fieldValue.simpleValue !== undefined) return fieldValue.simpleValue;
        return '';
    };

    const getEnumerationValues = () => {
        const fieldValue = getFacetValue();
        if (!fieldValue?.['restriction']) return [''];
        const restriction = fieldValue['restriction'] as Restriction;
        const enumValues = restriction['enumeration'] as RestrictionValue[] | undefined;
        if (!enumValues) return [''];
        return enumValues.map(item => item['@value'] || '');
    };

    const getPatternValue = () => {
        const fieldValue = getFacetValue();
        if (!fieldValue?.['restriction']) return '';
        const restriction = fieldValue['restriction'] as Restriction;
        const pattern = restriction['pattern'] as RestrictionValue[] | undefined;
        if (!pattern || !pattern.length) return '';
        return pattern[0]['@value'] || '';
    };

    const getRangeValues = () => {
        const fieldValue = getFacetValue();
        if (!fieldValue?.['restriction']) return { min: '', max: '', minType: 'Inclusive', maxType: 'Inclusive' };
        const restriction = fieldValue['restriction'] as Restriction;
        
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
        const fieldValue = getFacetValue();
        if (!fieldValue?.['restriction']) return '';
        const restriction = fieldValue['restriction'] as Restriction;
        const length = restriction['length'] as RestrictionValue[] | undefined;
        if (!length || !length.length) return '';
        return length[0]['@value'] || '';
    };

    const getLengthRangeValues = () => {
        const fieldValue = getFacetValue();
        if (!fieldValue?.['restriction']) return { min: '', max: '' };
        const restriction = fieldValue['restriction'] as Restriction;
        
        let min = '', max = '';
        
        if (restriction['minLength']?.length) {
            min = restriction['minLength'][0]['@value'] || '';
        }
        if (restriction['maxLength']?.length) {
            max = restriction['maxLength'][0]['@value'] || '';
        }
        
        return { min, max };
    };

    const setSimpleValue = (value: string) => {
        // For special properties (eg. @dataType), we set the value directly
        if (isSpecialProp) {
            setFieldValue(value);
            return;
        }
        setFieldValue({ simpleValue: value });
    };

    const setEnumerationValues = (values: string[]) => {
        const enumItems = values.filter(v => v && typeof v === 'string' && v.trim() !== '').map(v => ({ '@value': v }));
        setFieldValue({
            'restriction': {
                '@base': 'xs:string',
                'enumeration': enumItems
            }
        });
    };

    const setPatternValue = (value: string) => {
        setFieldValue({
            'restriction': {
                '@base': 'xs:string',
                'pattern': [{ '@value': value }]
            }
        });
    };

    const setRangeValues = (min: string, max: string, minType: string, maxType: string) => {
        const restriction: Restriction = { '@base': 'xs:string' };
        
        if (min !== '') {
            const minKey = minType === 'Inclusive' ? 'minInclusive' : 'minExclusive';
            (restriction as Record<string, RestrictionValue[]>)[minKey] = [{ '@value': min }];
        }
        if (max !== '') {
            const maxKey = maxType === 'Inclusive' ? 'maxInclusive' : 'maxExclusive';
            (restriction as Record<string, RestrictionValue[]>)[maxKey] = [{ '@value': max }];
        }
        
        setFieldValue({ 'restriction': restriction });
    };

    const setLengthValue = (value: string) => {
        setFieldValue({
            'restriction': {
                '@base': 'xs:string',
                'length': [{ '@value': value }]
            }
        });
    };

    const setLengthRangeValues = (min: string, max: string) => {
        const restriction: Restriction = { '@base': 'xs:string' };
        
        if (min !== '') restriction['minLength'] = [{ '@value': min }];
        if (max !== '') restriction['maxLength'] = [{ '@value': max }];
        
        setFieldValue({ 'restriction': restriction });
    };

    let restrictionType = $state(getRestrictionType());
    let hasUserSelectedType = $state(false);
    let lastFacetRef = $state(facet);
    let enumerationValues = $derived(getEnumerationValues());

    $effect(() => {
        if (facet !== lastFacetRef) {
            lastFacetRef = facet;
            hasUserSelectedType = false;
        }
        const detected = getRestrictionType();
        if (!hasUserSelectedType || detected !== 'Simple' || restrictionType === 'Simple') {
            restrictionType = detected;
        }
    });

    const handleTypeChange = (newType: string) => {
        hasUserSelectedType = true;
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

    const removeEnumerationValue = (index: number) => {
        enumerationValues = enumerationValues.filter((_, i) => i !== index);
        setEnumerationValues(enumerationValues);
    };

    const updateEnumerationValue = (index: number, value: string) => {
        enumerationValues[index] = value;
        setEnumerationValues(enumerationValues);
    };
</script>

<div class="form-group">
    <span class="form-label" id={`${baseId}-label`}>{label}</span>
    <div class="restriction-controls" role="group" aria-labelledby={`${baseId}-label`}>
        {#if !isSpecialProp}
            <div class="restriction-type-selector">
                <select
                    class="form-input"
                    bind:value={restrictionType}
                    onchange={(e) => handleTypeChange((e.target as HTMLSelectElement).value)}
                >
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
                    <input class="form-input" type="text" bind:value={() => getSimpleValue(), (v) => setSimpleValue(v)} {placeholder} aria-label={label}>
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
                                <input
                                    class="form-input"
                                    type="text"
                                    value={value}
                                    oninput={(e) => updateEnumerationValue(index, (e.target as HTMLInputElement).value)}
                                    {placeholder}
                                    aria-label={`${label} option ${index + 1}`}
                                >
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
                <input class="form-input" type="text" bind:value={() => getPatternValue(), (v) => setPatternValue(v)} placeholder="Enter regex pattern (e.g., DT[0-9]{2})" aria-label={`${label} pattern`}>
            
            {:else if restrictionType === 'Range'}
                {@const range = getRangeValues()}
                <div class="range-controls">
                    <div class="range-group">
                        <label for={`${baseId}-range-min`}>Min</label>
                        <input
                            class="form-input"
                            type="text"
                            id={`${baseId}-range-min`}
                            bind:value={() => range.min, (v) => setRangeValues(v, range.max, range.minType, range.maxType)}
                            placeholder="0"
                        >
                        <select
                            class="form-input"
                            aria-label="Min bound type"
                            bind:value={() => range.minType, (v) => setRangeValues(range.min, range.max, v, range.maxType)}
                        >
                            <option value="Inclusive">Inclusive</option>
                            <option value="Exclusive">Exclusive</option>
                        </select>
                    </div>
                    <div class="range-group">
                        <label for={`${baseId}-range-max`}>Max</label>
                        <input
                            class="form-input"
                            type="text"
                            id={`${baseId}-range-max`}
                            bind:value={() => range.max, (v) => setRangeValues(range.min, v, range.minType, range.maxType)}
                            placeholder="0"
                        >
                        <select
                            class="form-input"
                            aria-label="Max bound type"
                            bind:value={() => range.maxType, (v) => setRangeValues(range.min, range.max, range.minType, v)}
                        >
                            <option value="Inclusive">Inclusive</option>
                            <option value="Exclusive">Exclusive</option>
                        </select>
                    </div>
                </div>
            
            {:else if restrictionType === 'Length'}
                <input class="form-input" type="number" bind:value={() => getLengthValue(), (v) => setLengthValue(v)} placeholder="Enter exact length" aria-label={`${label} length`}>
            
            {:else if restrictionType === 'Length Range'}
                {@const lengthRange = getLengthRangeValues()}
                <div class="length-range-controls">
                    <div class="length-group">
                        <label for={`${baseId}-length-min`}>Min Length</label>
                        <input class="form-input" id={`${baseId}-length-min`} type="number" bind:value={() => lengthRange.min, (v) => setLengthRangeValues(v, lengthRange.max)} placeholder="0">
                    </div>
                    <div class="length-group">
                        <label for={`${baseId}-length-max`}>Max Length</label>
                        <input class="form-input" id={`${baseId}-length-max`} type="number" bind:value={() => lengthRange.max, (v) => setLengthRangeValues(lengthRange.min, v)} placeholder="0">
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
