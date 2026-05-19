<script lang="ts">
	import { Menubar as MenubarPrimitive } from "bits-ui";

	type Props = {
		ref?: HTMLElement | null;
	} & Record<string, unknown>;

	let {
		ref = $bindable(null),
		...restProps
	} : Props = $props();
</script>

<MenubarPrimitive.Group bind:ref data-slot="menubar-group" {...restProps} />
