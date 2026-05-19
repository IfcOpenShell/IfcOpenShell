<script lang="ts">
	import { Menubar as MenubarPrimitive } from "bits-ui";
	import { cn } from "$lib/utils";

	type Props = {
		ref?: HTMLElement | null;
		class?: string;
	} & Record<string, unknown>;

	let {
		ref = $bindable(null),
		class: className,
		...restProps
	} : Props = $props();
</script>

<MenubarPrimitive.Root
	bind:ref
	data-slot="menubar"
	class={cn(
		"flex h-9 items-center gap-1 rounded-md p-1",
		className
	)}
	{...restProps}
/>
