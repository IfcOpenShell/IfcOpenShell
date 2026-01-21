<script lang="ts">
	import { cn } from "$lib/utils";
	import { Menubar as MenubarPrimitive } from "bits-ui";
	type Props = {
		ref?: HTMLElement | null;
		inset?: boolean;
		class?: string;
	} & Record<string, unknown>;
	let {
		ref = $bindable(null),
		inset,
		class: className,
		...restProps
	} : Props = $props();
</script>

<MenubarPrimitive.GroupHeading
	bind:ref
	data-slot="menubar-group-heading"
	data-inset={inset}
	class={cn("px-2 py-1.5 text-sm font-medium data-[inset]:pl-8", className)}
	{...restProps}
/>
