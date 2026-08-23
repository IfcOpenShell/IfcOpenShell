
export interface NativeHandle {
  destroy(): void;
}

export class HandleGuard<T extends NativeHandle> {
  readonly #token = {};

  constructor(
    owner: object,
    private raw: T | null,
    private readonly owned: boolean,
  ) {
    if (owned && raw !== null) finalizers?.register(owner, raw, this.#token);
  }

  release(): T | null {
    const raw = this.raw;
    this.raw = null;
    if (this.owned) finalizers?.unregister(this.#token);
    return raw;
  }

  destroy(): void {
    const raw = this.release();
    if (this.owned) raw?.destroy();
  }
}

const finalizers = typeof FinalizationRegistry === 'function'
  ? new FinalizationRegistry<NativeHandle>((raw) => destroy(raw))
  : null;

export function destroyFinalized(raw: NativeHandle | null): void {
  destroy(raw);
}

function destroy(raw: NativeHandle | null): void {
  try {
    raw?.destroy();
  } catch {
    // Finalizers may run during runtime teardown; explicit dispose reports errors earlier.
  }
}
