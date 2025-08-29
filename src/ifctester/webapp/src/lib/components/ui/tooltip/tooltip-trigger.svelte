<script>
	import { Tooltip as TooltipPrimitive } from "bits-ui";

	let { ref = $bindable(null), ...restProps } = $props();
</script>

<TooltipPrimitive.Trigger bind:ref data-slot="tooltip-trigger" {...restProps} />