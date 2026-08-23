
import { describe, expect, it, vi } from 'vitest';
import { HandleGuard, destroyFinalized } from '../src/resource.js';

describe('HandleGuard', () => {
  it('destroys owned handles on explicit disposal', () => {
    const raw = { destroy: vi.fn() };
    const guard = new HandleGuard({}, raw, true);

    guard.destroy();

    expect(raw.destroy).toHaveBeenCalledOnce();
  });

  it('does not destroy borrowed handles', () => {
    const raw = { destroy: vi.fn() };
    const guard = new HandleGuard({}, raw, false);

    guard.destroy();

    expect(raw.destroy).not.toHaveBeenCalled();
  });

  it('reports explicit destroy errors', () => {
    const raw = {
      destroy: vi.fn(() => {
        throw new Error('destroy failed');
      }),
    };
    const guard = new HandleGuard({}, raw, true);

    expect(() => guard.destroy()).toThrow('destroy failed');
  });

  it('keeps finalizer cleanup best-effort', () => {
    const raw = {
      destroy: vi.fn(() => {
        throw new Error('destroy failed');
      }),
    };

    expect(() => destroyFinalized(raw)).not.toThrow();
    expect(raw.destroy).toHaveBeenCalledOnce();
  });
});
