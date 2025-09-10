<script>
	import { Menubar as MenubarPrimitive } from "bits-ui";

	let {
		ref = $bindable(null),
		...restProps
	} = $props();
</script>

<MenubarPrimitive.Group bind:ref data-slot="menubar-group" {...restProps} />