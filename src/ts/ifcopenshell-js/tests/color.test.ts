
import { describe, it, expect } from 'vitest';
import { hashColor, meshColor } from '../src/util/color.js';

describe('hashColor', () => {
  it('is deterministic for the same input', () => {
    const a = hashColor('IfcWall');
    const b = hashColor('IfcWall');
    expect(b).toEqual(a);
  });

  it('produces three components in [0, 1]', () => {
    const [r, g, b] = hashColor('IfcSlab');
    expect(r).toBeGreaterThanOrEqual(0);
    expect(r).toBeLessThanOrEqual(1);
    expect(g).toBeGreaterThanOrEqual(0);
    expect(g).toBeLessThanOrEqual(1);
    expect(b).toBeGreaterThanOrEqual(0);
    expect(b).toBeLessThanOrEqual(1);
  });

  it('differs for distinct inputs', () => {
    expect(hashColor('IfcWall')).not.toEqual(hashColor('IfcSlab'));
  });
});

describe('meshColor', () => {
  it('falls back to a type-hash color when no materials are present', () => {
    const c = meshColor('IfcWall', [], []);
    expect(c).toEqual(hashColor('IfcWall'));
  });

  it('reads the first material RGBA when available', () => {
    const colors = [0.1, 0.2, 0.3, 1.0, 0.4, 0.5, 0.6, 1.0];
    const c = meshColor('IfcWall', [1], colors);
    expect(c).toEqual([0.4, 0.5, 0.6]);
  });

  it('falls back to a hash when the material color buffer is too short', () => {
    expect(meshColor('IfcWall', [0], [])).toEqual(hashColor('IfcWall'));
  });
});
