<script lang="ts">
	import { DropdownMenu as DropdownMenuPrimitive } from "bits-ui";
	import { cn } from "$lib/utils";
	type Props = {
		ref?: HTMLElement | null;
		class?: string;
		inset?: boolean;
	} & Record<string, unknown>;
	let {
		ref = $bindable(null),
		class: className,
		inset,
		...restProps
	} : Props = $props();
</script>

<DropdownMenuPrimitive.GroupHeading
	bind:ref
	data-slot="dropdown-menu-group-heading"
	data-inset={inset}
	class={cn("px-2 py-1.5 text-sm font-semibold data-[inset]:pl-8", className)}
	{...restProps}
/>
