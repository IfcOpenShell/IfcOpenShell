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

<DialogPrimitive.Title
	bind:ref
	data-slot="dialog-title"
	class={cn("text-lg leading-none", className)}
	{...restProps}
/>
