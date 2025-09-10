<script>
	import { Menubar as MenubarPrimitive } from "bits-ui";
	import { cn } from "$lib/utils.js";

	let {
		ref = $bindable(null),
		class: className,
		...restProps
	} = $props();
</script>

<MenubarPrimitive.Separator
	bind:ref
	data-slot="menubar-separator"
	class={cn("bg-border -mx-1 my-1 h-px", className)}
	{...restProps}
/>