<script lang="ts">
	import { Tooltip as TooltipPrimitive } from "bits-ui";

	type Props = {
		ref?: HTMLElement | null;
	} & Record<string, unknown>;

	let { ref = $bindable(null), ...restProps } : Props = $props();
</script>

<TooltipPrimitive.Trigger bind:ref data-slot="tooltip-trigger" {...restProps} />
