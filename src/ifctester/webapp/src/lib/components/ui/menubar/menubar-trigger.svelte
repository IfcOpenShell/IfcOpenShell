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

<MenubarPrimitive.Trigger
	bind:ref
	data-slot="menubar-trigger"
	class={cn(
		"data-[state=open]:bg-accent data-[state=open]:text-accent-foreground outline-hidden flex select-none items-center rounded-sm px-2 py-1 text-sm font-medium",
		className
	)}
	{...restProps}
/>
