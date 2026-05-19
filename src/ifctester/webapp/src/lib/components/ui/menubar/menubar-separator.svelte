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

<MenubarPrimitive.Separator
	bind:ref
	data-slot="menubar-separator"
	class={cn("bg-border -mx-1 my-1 h-px", className)}
	{...restProps}
/>
