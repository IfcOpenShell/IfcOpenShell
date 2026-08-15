import { describe, expect, it } from 'vitest';
import {
  columnMajorToRowMajor4,
  rowMajorToColumnMajor4,
  transformPoint4,
} from '../../src/index.js';

describe('geometry matrix helpers', () => {
  const identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];

  it('preserves identity and Float64 precision', () => {
    const converted = rowMajorToColumnMajor4(identity);
    expect(converted).toBeInstanceOf(Float64Array);
    expect([...converted]).toEqual(identity);
  });

  it('converts translation and rotation layouts', () => {
    const rowMajor = [
      0, -1, 0, 10,
      1, 0, 0, 20,
      0, 0, 1, 30,
      0, 0, 0, 1,
    ];
    const columnMajor = rowMajorToColumnMajor4(rowMajor);
    expect([...columnMajor]).toEqual([
      0, 1, 0, 0,
      -1, 0, 0, 0,
      0, 0, 1, 0,
      10, 20, 30, 1,
    ]);
    expect(transformPoint4(columnMajor, [2, 3, 4])).toEqual([7, 22, 34]);
    expect([...columnMajorToRowMajor4(columnMajor)]).toEqual(rowMajor);
  });

  it('rejects malformed matrices', () => {
    expect(() => rowMajorToColumnMajor4([1, 2, 3])).toThrow(/16-element row-major Matrix4/);
    expect(() => columnMajorToRowMajor4([])).toThrow(/16-element column-major Matrix4/);
    expect(() => transformPoint4(new Float64Array(15), [0, 0, 0])).toThrow(/16-element/);
    expect(() => transformPoint4(new Float64Array(16), [0, 0, 0])).toThrow(/homogeneous coordinate is zero/);
  });
});
