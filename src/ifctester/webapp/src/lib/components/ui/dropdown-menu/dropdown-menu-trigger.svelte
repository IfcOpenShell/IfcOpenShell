<script lang="ts">
	import { DropdownMenu as DropdownMenuPrimitive } from "bits-ui";

	type Props = {
		ref?: HTMLElement | null;
	} & Record<string, unknown>;

	let { ref = $bindable(null), ...restProps } : Props = $props();
</script>

<DropdownMenuPrimitive.Trigger bind:ref data-slot="dropdown-menu-trigger" {...restProps} />
