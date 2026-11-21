<script lang="ts">
    import * as Dialog from "$lib/components/ui/dialog";
    import { testPattern } from "$src/modules/api/api.svelte";

    let {
        open = $bindable(false),
        initialPattern = ""
    }: {
        open?: boolean;
        initialPattern?: string;
    } = $props();

    let pattern = $state("");
    let valuesText = $state("");
    let results = $state<{ value: string; passes: boolean }[]>([]);
    let patternError = $state<string | null>(null);
    let isChecking = $state(false);
    let requestToken = 0;

    let hasAnchors = $derived(pattern.includes("^") || pattern.includes("$"));
    let sampleValues = $derived(valuesText.split("\n").filter((value) => value !== ""));

    // Seed the pattern from the editor each time the dialog is opened
    $effect(() => {
        if (open) pattern = initialPattern;
    });

    // Debounced live evaluation through ifctester in the Pyodide worker
    $effect(() => {
        if (!open) return;
        const currentPattern = pattern;
        const currentValues = sampleValues;

        if (currentPattern === "" || currentValues.length === 0) {
            requestToken++;
            results = [];
            patternError = null;
            isChecking = false;
            return;
        }

        const token = ++requestToken;
        const timer = setTimeout(async () => {
            isChecking = true;
            try {
                const response = await testPattern(currentPattern, currentValues);
                if (token !== requestToken) return;
                patternError = response.error;
                results = response.error
                    ? []
                    : currentValues.map((value, index) => ({ value, passes: response.results[index] }));
            } catch (err) {
                if (token !== requestToken) return;
                patternError = err instanceof Error ? err.message : String(err);
                results = [];
            } finally {
                if (token === requestToken) isChecking = false;
            }
        }, 300);

        return () => clearTimeout(timer);
    });
</script>

<Dialog.Root bind:open={open}>
    <Dialog.Content class="sm:max-w-[550px]">
        <Dialog.Header>
            <Dialog.Title>Pattern Playground</Dialog.Title>
            <Dialog.Description>
                Patterns are checked by ifctester itself, so the verdicts match a real IDS audit.
            </Dialog.Description>
        </Dialog.Header>
        <div class="playground">
            <div class="form-group">
                <label for="playground-pattern">XSD Pattern</label>
                <input
                    class="form-input"
                    id="playground-pattern"
                    type="text"
                    bind:value={pattern}
                    placeholder="e.g., DT[0-9]{2}"
                >
                <p class="hint">Note: IDS patterns must match the whole value, not just a part of it.</p>
                {#if hasAnchors}
                    <p class="warning">
                        Warning: ^ and $ anchors are not part of IDS pattern syntax (XSD regex) and behave
                        differently across validators. Remove them; patterns already match the whole value.
                    </p>
                {/if}
                {#if patternError}
                    <p class="pattern-error">Invalid pattern: {patternError}</p>
                {/if}
            </div>
            <div class="form-group">
                <label for="playground-values">Sample Values (one per line)</label>
                <textarea
                    class="form-input"
                    id="playground-values"
                    rows="4"
                    bind:value={valuesText}
                    placeholder="DT01&#10;DT1"
                ></textarea>
            </div>
            {#if results.length > 0 && !patternError}
                <ul class="results" class:checking={isChecking}>
                    {#each results as result}
                        <li class="result-item">
                            <span class="verdict {result.passes ? 'pass' : 'fail'}">
                                {result.passes ? 'PASS' : 'FAIL'}
                            </span>
                            <span class="result-value">{result.value}</span>
                        </li>
                    {/each}
                </ul>
            {/if}
        </div>
        <Dialog.Footer>
            <Dialog.Close asChild>
                <button class="btn">Close</button>
            </Dialog.Close>
        </Dialog.Footer>
    </Dialog.Content>
</Dialog.Root>

<style>
    .playground {
        display: flex;
        flex-direction: column;
        gap: 14px;
    }

    .hint {
        font-size: 12px;
        color: #999;
        margin: 4px 0 0;
    }

    .warning {
        font-size: 12px;
        color: #e8a33d;
        margin: 4px 0 0;
    }

    .pattern-error {
        font-size: 12px;
        color: #e05d5d;
        margin: 4px 0 0;
    }

    .results {
        list-style: none;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        gap: 6px;
        max-height: 200px;
        overflow-y: auto;
    }

    .results.checking {
        opacity: 0.6;
    }

    .result-item {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .verdict {
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        min-width: 44px;
        text-align: center;
    }

    .verdict.pass {
        background: #1f4d2e;
        color: #7fdc9a;
    }

    .verdict.fail {
        background: #542125;
        color: #f0868c;
    }

    .result-value {
        font-family: monospace;
        font-size: 13px;
        word-break: break-all;
    }
</style>
