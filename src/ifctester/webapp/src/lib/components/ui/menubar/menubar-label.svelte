<script lang="ts">
	import { cn } from "$lib/utils";
	import type { Snippet } from "svelte";
	type Props = {
		ref?: HTMLElement | null;
		inset?: boolean;
		children?: Snippet;
		class?: string;
	} & Record<string, unknown>;
	let {
		ref = $bindable(null),
		inset,
		children,
		class: className,
		...restProps
	} : Props = $props();
</script>

<div
	bind:this={ref}
	data-slot="menubar-label"
	data-inset={inset}
	class={cn("px-2 py-1.5 text-sm font-medium data-[inset]:pl-8", className)}
	{...restProps}
>
	{@render children?.()}
</div>
