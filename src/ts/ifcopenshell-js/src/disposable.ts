
/**
 * Make explicit-resource-management symbols available to consumers that do
 * not opt into TypeScript's `ESNext.Disposable` library themselves.
 */
declare global {
  interface SymbolConstructor {
    readonly dispose: unique symbol;
    readonly asyncDispose: unique symbol;
  }
}

export {};
