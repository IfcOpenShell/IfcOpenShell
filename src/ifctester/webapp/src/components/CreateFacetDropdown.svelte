<script>
    import * as DropdownMenu from "$lib/components/ui/dropdown-menu";

    let { addFacet } = $props();
</script>

<DropdownMenu.Root>
    <DropdownMenu.Trigger class="btn">
        Create Facet
        <svg class="ml-2 h-4 w-4" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6,9 12,15 18,9"></polyline>
        </svg>
    </DropdownMenu.Trigger>
    <DropdownMenu.Content class="w-56">
        <DropdownMenu.Item onclick={() => addFacet('entity')}>
            <svg class="mr-2 h-4 w-4" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="9" cy="9" r="2"></circle>
                <path d="M21 15.5c-3-3.5-10-3.5-13 0"></path>
            </svg>
            Entity
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => addFacet('attribute')}>
            <svg class="mr-2 h-4 w-4" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
            </svg>
            Attribute
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => addFacet('property')}>
            <svg class="mr-2 h-4 w-4" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M8 2v4"></path>
                <path d="M16 2v4"></path>
                <rect x="3" y="4" width="18" height="18" rx="2"></rect>
                <path d="M3 10h18"></path>
            </svg>
            Property
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => addFacet('material')}>
            <svg class="mr-2 h-4 w-4" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                <path d="M2 17l10 5 10-5"></path>
                <path d="M2 12l10 5 10-5"></path>
            </svg>
            Material
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => addFacet('classification')}>
            <svg class="mr-2 h-4 w-4" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
            Classification
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => addFacet('partOf')}>
            <svg class="mr-2 h-4 w-4" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6"></path>
                <path d="M5.636 5.636l4.242 4.242m4.242 4.242l4.242 4.242"></path>
                <path d="M18.364 5.636l-4.242 4.242m-4.242 4.242L5.636 18.364"></path>
            </svg>
            Part Of
        </DropdownMenu.Item>
    </DropdownMenu.Content>
</DropdownMenu.Root>