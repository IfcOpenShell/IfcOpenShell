<script lang="ts">
	import { Dialog as DialogPrimitive } from "bits-ui";
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

<DialogPrimitive.Description
	bind:ref
	data-slot="dialog-description"
	class={cn("text-muted-foreground text-sm", className)}
	{...restProps}
/>
