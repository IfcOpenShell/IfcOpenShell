<script lang="ts">
	import { cn } from "$lib/utils";
	import type { Snippet } from "svelte";

	type Props = {
		ref?: HTMLElement | null;
		class?: string;
		children?: Snippet;
	} & Record<string, unknown>;

	let {
		ref = $bindable(null),
		class: className,
		children,
		...restProps
	} : Props = $props();
</script>

<div
	bind:this={ref}
	data-slot="dialog-footer"
	class={cn("flex flex-col-reverse gap-2 sm:flex-row sm:justify-end", className)}
	{...restProps}
>
	{@render children?.()}
</div>
