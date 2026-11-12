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

<span
	bind:this={ref}
	data-slot="menubar-shortcut"
	class={cn("text-muted-foreground ml-auto text-xs tracking-widest", className)}
	{...restProps}
>
	{@render children?.()}
</span>
