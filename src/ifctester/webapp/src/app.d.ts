declare module "*.svelte" {
    import type { SvelteComponent } from "svelte";
    export default class Component extends SvelteComponent {}
}
