<script lang="ts">
	import { DropdownMenu as DropdownMenuPrimitive } from "bits-ui";

	type Props = {
		ref?: HTMLElement | null;
		value?: string;
	} & Record<string, unknown>;

	let {
		ref = $bindable(null),
		value = $bindable(),
		...restProps
	} : Props = $props();
</script>

<DropdownMenuPrimitive.RadioGroup
	bind:ref
	bind:value
	data-slot="dropdown-menu-radio-group"
	{...restProps}
/>
