// This file was generated with the assistance of an AI coding tool.
// SPDX-License-Identifier: LGPL-3.0-or-later

// The subset of numpy that ifcopenshell.util and ifcopenshell.api use, for generated code:
// strided n-dimensional arrays whose slices are views, broadcasting arithmetic through Python's
// operator protocol (see _py.ts), and the vector and matrix functions those modules call.
// Function names are camelCase (np.zeros_like is zerosLike); keyword arguments are a trailing
// options object. Hand-written, unlike the transpiled util/ and api/ next to it.

import { hooks, IndexList, NotImplemented, Slice } from './_py.js';

type DType = 'float64' | 'int64' | 'bool' | 'object';
type Options = Record<string, any>;
export type ArrayLike = NDArray | number | boolean | ArrayLike[] | Iterable<unknown>;

const isOptions = (value: unknown): value is Options =>
  value !== null && typeof value === 'object' && Object.getPrototypeOf(value) === Object.prototype;

/** Trailing options object of a call, if any. */
function options(values: unknown[]): Options {
  return isOptions(values[values.length - 1]) ? (values.pop() as Options) : {};
}

const product = (shape: number[]) => shape.reduce((a, b) => a * b, 1);
const contiguous = (shape: number[]) => {
  const strides = new Array<number>(shape.length);
  let stride = 1;
  for (let i = shape.length - 1; i >= 0; i--) {
    strides[i] = stride;
    stride *= shape[i]!;
  }
  return strides;
};

function dtypeName(dtype: unknown): DType | undefined {
  if (dtype === undefined || dtype === null) return undefined;
  if (dtype === Boolean || dtype === 'bool' || dtype === bool_) return 'bool';
  if (dtype === 'int' || dtype === 'int64' || dtype === 'int32' || dtype === int64 || dtype === int32 || dtype === intc) return 'int64';
  if (dtype === 'object' || dtype === Object) return 'object';
  return 'float64';
}

function cast(value: any, dtype: DType): any {
  if (dtype === 'bool') return Boolean(value);
  if (dtype === 'int64') return Math.trunc(Number(value));
  if (dtype === 'float64') return typeof value === 'boolean' ? Number(value) : Number(value);
  return value;
}

/** numpy.ndarray: `data` with a shape, strides and offset, so that slices and transposes are views. */
export class NDArray {
  constructor(
    public data: any[],
    readonly shape: number[],
    readonly strides: number[] = contiguous(shape),
    readonly offset = 0,
    public dtype: DType = 'float64',
  ) {}

  get ndim(): number {
    return this.shape.length;
  }

  get size(): number {
    return product(this.shape);
  }

  get T(): NDArray {
    return this.transpose();
  }

  /** Element positions in `data`, in C (row-major) order. */
  positions(): number[] {
    const result: number[] = [];
    const walk = (axis: number, position: number) => {
      if (axis === this.ndim) {
        result.push(position);
        return;
      }
      for (let i = 0; i < this.shape[axis]!; i++) walk(axis + 1, position + i * this.strides[axis]!);
    };
    walk(0, this.offset);
    return result;
  }

  /** Elements in C order. */
  values(): any[] {
    return this.positions().map(p => this.data[p]);
  }

  __len__(): number {
    if (!this.ndim) throw new TypeError('len() of unsized object');
    return this.shape[0]!;
  }

  __bool__(): boolean {
    if (this.size !== 1) throw new Error('ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()');
    return Boolean(this.data[this.positions()[0]!]);
  }

  *[Symbol.iterator](): IterableIterator<any> {
    if (!this.ndim) throw new TypeError('iteration over a 0-d array');
    for (let i = 0; i < this.shape[0]!; i++) yield this.__getitem__(i);
  }

  __contains__(value: unknown): boolean {
    return this.values().some(v => v === value);
  }

  // Indexing.

  /** Basic indexing gives a view (or a scalar); integer and boolean array indices give a copy. */
  __getitem__(key: unknown): any {
    const advanced = advancedIndex(this, key);
    if (advanced) return advanced;
    const view = this.view(key);
    return view.ndim === 0 ? view.data[view.offset] : view;
  }

  __setitem__(key: unknown, value: unknown): void {
    const mask = asMask(this, key);
    if (mask) {
      const positions = this.positions().filter((_, i) => mask[i]);
      const source = asarray(value as ArrayLike);
      const values = source.size === 1 ? positions.map(() => source.values()[0]) : source.values();
      positions.forEach((p, i) => (this.data[p] = cast(values[i], this.dtype)));
      return;
    }
    if (isIndexArray(key)) {
      const rows = indexList(key, this.shape[0]!);
      const source = broadcastTo(asarray(value as ArrayLike), [rows.length, ...this.shape.slice(1)]);
      rows.forEach((row, i) => this.view(row).assign(source.__getitem__(i)));
      return;
    }
    this.view(key).assign(value);
  }

  /** Write values into this array (a view), broadcasting them to its shape. */
  assign(value: unknown): void {
    const source = broadcastTo(asarray(value as ArrayLike), this.shape).values();
    this.positions().forEach((p, i) => (this.data[p] = cast(source[i], this.dtype)));
  }

  private view(key: unknown): NDArray {
    const keys = Array.isArray(key) ? [...key] : [key];
    const ellipsis = keys.indexOf(undefined);
    const used = keys.filter(k => k !== null && k !== undefined).length;
    if (ellipsis >= 0) keys.splice(ellipsis, 1, ...new Array(Math.max(0, this.ndim - used)).fill(new Slice(null, null, null)));
    if (used > this.ndim) throw new Error(`IndexError: too many indices for array: array is ${this.ndim}-dimensional, but ${used} were indexed`);
    const shape: number[] = [];
    const strides: number[] = [];
    let offset = this.offset;
    let axis = 0;
    for (const k of keys) {
      if (k === null) {
        shape.push(1);
        strides.push(0);
      } else if (k instanceof Slice) {
        const [start, , step] = k.indices(this.shape[axis]!);
        const count = k.range(this.shape[axis]!).length;
        offset += start * this.strides[axis]!;
        shape.push(count);
        strides.push(step * this.strides[axis]!);
        axis++;
      } else {
        const index = Number(k);
        const length = this.shape[axis]!;
        const position = index < 0 ? index + length : index;
        if (!Number.isInteger(position) || position < 0 || position >= length) {
          throw new Error(`IndexError: index ${index} is out of bounds for axis ${axis} with size ${length}`);
        }
        offset += position * this.strides[axis]!;
        axis++;
      }
    }
    for (; axis < this.ndim; axis++) {
      shape.push(this.shape[axis]!);
      strides.push(this.strides[axis]!);
    }
    return new NDArray(this.data, shape, strides, offset, this.dtype);
  }

  // Conversions and shape.

  tolist(): any {
    const convert = (value: any) => (this.dtype === 'bool' ? Boolean(value) : value);
    if (!this.ndim) return convert(this.data[this.offset]);
    const build = (axis: number, position: number): any[] =>
      Array.from({ length: this.shape[axis]! }, (_, i) => {
        const p = position + i * this.strides[axis]!;
        return axis === this.ndim - 1 ? convert(this.data[p]) : build(axis + 1, p);
      });
    return build(0, this.offset);
  }

  item(...index: number[]): any {
    if (!index.length) {
      if (this.size !== 1) throw new Error('ValueError: can only convert an array of size 1 to a Python scalar');
      return this.tolist() instanceof Array ? this.values()[0] : this.tolist();
    }
    return this.view(index).data[this.view(index).offset];
  }

  copy(): NDArray {
    return new NDArray(this.values(), [...this.shape], undefined, 0, this.dtype);
  }

  astype(dtype: unknown): NDArray {
    const type = dtypeName(dtype) ?? 'float64';
    return new NDArray(this.values().map(v => cast(v, type)), [...this.shape], undefined, 0, type);
  }

  reshape(...values: any[]): NDArray {
    const { order = 'C' } = options(values);
    let shape: number[] = values.length === 1 && typeof values[0] !== 'number' ? Array.from(values[0]) : values;
    const known = product(shape.filter(n => n >= 0));
    shape = shape.map(n => (n < 0 ? this.size / known : n));
    if (product(shape) !== this.size) throw new Error(`ValueError: cannot reshape array of size ${this.size} into shape (${shape.join(', ')})`);
    if (order === 'F') {
      // Fill the new shape in column-major order from the column-major elements.
      const source = this.transpose().values();
      const reversed = new NDArray(source, [...shape].reverse(), undefined, 0, this.dtype);
      return reversed.transpose().copy();
    }
    return new NDArray(this.values(), shape, undefined, 0, this.dtype);
  }

  flatten(): NDArray {
    return new NDArray(this.values(), [this.size], undefined, 0, this.dtype);
  }

  ravel(): NDArray {
    return this.flatten();
  }

  transpose(...axes: number[]): NDArray {
    const order = axes.length ? (Array.isArray(axes[0]) ? (axes[0] as unknown as number[]) : axes) : this.shape.map((_, i) => this.ndim - 1 - i);
    return new NDArray(this.data, order.map(i => this.shape[i]!), order.map(i => this.strides[i]!), this.offset, this.dtype);
  }

  dot(other: ArrayLike): any {
    return dot(this, other);
  }

  cross(other: ArrayLike): any {
    return cross(this, other);
  }

  sum(...values: unknown[]): any {
    return sum(this, ...values);
  }

  min(...values: unknown[]): any {
    return min(this, ...values);
  }

  max(...values: unknown[]): any {
    return max(this, ...values);
  }

  mean(...values: unknown[]): any {
    return mean(this, ...values);
  }

  any(...values: unknown[]): any {
    return any(this, ...values);
  }

  all(...values: unknown[]): any {
    return all(this, ...values);
  }

  round(decimals = 0): NDArray {
    return round(this, decimals) as NDArray;
  }

  clip(lower: number | null, upper: number | null): NDArray {
    return clip(this, lower, upper) as NDArray;
  }

  argmax(): number {
    return argmax(this);
  }

  argmin(): number {
    return argmin(this);
  }

  toString(): string {
    return `array(${JSON.stringify(this.tolist())})`;
  }

  // Python operators; see _py.ts.

  __add__(other: unknown) { return binary(this, other, (a, b) => a + b); }
  __radd__(other: unknown) { return binary(other, this, (a, b) => a + b); }
  __sub__(other: unknown) { return binary(this, other, (a, b) => a - b); }
  __rsub__(other: unknown) { return binary(other, this, (a, b) => a - b); }
  __mul__(other: unknown) { return binary(this, other, (a, b) => a * b); }
  __rmul__(other: unknown) { return binary(other, this, (a, b) => a * b); }
  __truediv__(other: unknown) { return binary(this, other, (a, b) => a / b, 'float64'); }
  __rtruediv__(other: unknown) { return binary(other, this, (a, b) => a / b, 'float64'); }
  __floordiv__(other: unknown) { return binary(this, other, (a, b) => Math.floor(a / b)); }
  __rfloordiv__(other: unknown) { return binary(other, this, (a, b) => Math.floor(a / b)); }
  __mod__(other: unknown) { return binary(this, other, (a, b) => ((a % b) + b) % b); }
  __pow__(other: unknown) { return binary(this, other, (a, b) => a ** b); }
  __rpow__(other: unknown) { return binary(other, this, (a, b) => a ** b); }
  __matmul__(other: unknown) { return operand(other) ? matmul(this, other as ArrayLike) : NotImplemented; }
  __rmatmul__(other: unknown) { return operand(other) ? matmul(other as ArrayLike, this) : NotImplemented; }
  __neg__() { return unary(this, a => -a); }
  __abs__() { return unary(this, Math.abs); }
  __eq__(other: unknown) { return binary(this, other, (a, b) => a === b, 'bool'); }
  __ne__(other: unknown) { return binary(this, other, (a, b) => a !== b, 'bool'); }
  __lt__(other: unknown) { return binary(this, other, (a, b) => a < b, 'bool'); }
  __le__(other: unknown) { return binary(this, other, (a, b) => a <= b, 'bool'); }
  __gt__(other: unknown) { return binary(this, other, (a, b) => a > b, 'bool'); }
  __ge__(other: unknown) { return binary(this, other, (a, b) => a >= b, 'bool'); }
  __iadd__(other: unknown) { return this.inplace(this.__add__(other)); }
  __isub__(other: unknown) { return this.inplace(this.__sub__(other)); }
  __imul__(other: unknown) { return this.inplace(this.__mul__(other)); }
  __itruediv__(other: unknown) { return this.inplace(this.__truediv__(other)); }

  private inplace(result: unknown): unknown {
    if (result === NotImplemented) return result;
    this.assign(result);
    return this;
  }
}

/** Values that arithmetic with arrays accepts: numbers, booleans, arrays and (nested) lists. */
const operand = (value: unknown) => typeof value === 'number' || typeof value === 'boolean' || value instanceof NDArray || Array.isArray(value);

function broadcastShape(a: number[], b: number[]): number[] {
  const length = Math.max(a.length, b.length);
  return Array.from({ length }, (_, i) => {
    const x = a[a.length - length + i] ?? 1;
    const y = b[b.length - length + i] ?? 1;
    if (x !== y && x !== 1 && y !== 1) throw new Error(`ValueError: operands could not be broadcast together with shapes (${a}) (${b})`);
    return x === 1 ? y : x;
  });
}

/** A view of `array` repeated (with zero strides) to `shape`. */
function broadcastTo(array: NDArray, shape: number[]): NDArray {
  const target = broadcastShape(array.shape, shape);
  if (target.length !== shape.length || target.some((n, i) => n !== shape[i])) {
    throw new Error(`ValueError: could not broadcast input array from shape (${array.shape}) into shape (${shape})`);
  }
  const extra = shape.length - array.ndim;
  const strides = shape.map((n, i) => (i < extra || array.shape[i - extra] === 1 && n !== 1 ? 0 : array.strides[i - extra]!));
  return new NDArray(array.data, shape, strides, array.offset, array.dtype);
}

function resultType(a: NDArray, b: NDArray): DType {
  if (a.dtype === 'object' || b.dtype === 'object') return 'object';
  if (a.dtype === 'float64' || b.dtype === 'float64') return 'float64';
  if (a.dtype === 'int64' || b.dtype === 'int64') return 'int64';
  return 'bool';
}

function binary(left: unknown, right: unknown, f: (a: any, b: any) => any, dtype?: DType): any {
  if (!operand(left) || !operand(right)) return NotImplemented;
  const a = asarray(left as ArrayLike);
  const b = asarray(right as ArrayLike);
  const shape = broadcastShape(a.shape, b.shape);
  const x = broadcastTo(a, shape).values();
  const y = broadcastTo(b, shape).values();
  let type = dtype ?? resultType(a, b);
  const raw = x.map((value, i) => f(value, y[i]));
  if (type === 'int64' && raw.some(v => !Number.isInteger(v))) type = 'float64';
  const data = raw.map(v => cast(v, type));
  const result = new NDArray(data, shape, undefined, 0, type);
  return shape.length ? result : data[0];
}

function unary(value: ArrayLike, f: (a: number) => any, dtype?: DType): any {
  if (typeof value === 'number' || typeof value === 'boolean') return f(Number(value));
  const array = asarray(value);
  return new NDArray(array.values().map(v => f(v)), [...array.shape], undefined, 0, dtype ?? (array.dtype === 'int64' ? 'float64' : array.dtype));
}

function isIndexArray(key: unknown): boolean {
  return key instanceof NDArray || key instanceof IndexList;
}

function asMask(array: NDArray, key: unknown): boolean[] | null {
  if (!(key instanceof NDArray) || key.dtype !== 'bool') return null;
  if (key.size !== array.size) throw new Error('IndexError: boolean index did not match indexed array');
  return key.values().map(Boolean);
}

function indexList(key: unknown, length: number): number[] {
  const items = key instanceof IndexList ? key.items : (key as NDArray).values();
  return items.map(i => {
    const index = Number(i);
    return index < 0 ? index + length : index;
  });
}

function advancedIndex(array: NDArray, key: unknown): NDArray | null {
  const mask = asMask(array, key);
  if (mask) return new NDArray(array.values().filter((_, i) => mask[i]), [mask.filter(Boolean).length], undefined, 0, array.dtype);
  if (!isIndexArray(key)) return null;
  const rows = indexList(key, array.shape[0]!).map(i => asarray(array.__getitem__(i)));
  return stack(rows);
}

// Construction.

/** numpy.array / numpy.asarray: nested lists (or arrays) of numbers. */
export function array(value: ArrayLike, ...values: unknown[]): NDArray {
  const { dtype, copy = true } = { ...options(values), ...(values.length ? { dtype: values[0] } : {}) } as Options;
  const type = dtypeName(dtype);
  if (value instanceof NDArray) {
    const result = type && type !== value.dtype ? value.astype(type) : copy ? value.copy() : value;
    return result;
  }
  const shape: number[] = [];
  const data: any[] = [];
  const walk = (item: any, depth: number) => {
    const isSequence = item instanceof NDArray || Array.isArray(item) || (item !== null && typeof item === 'object' && typeof item[Symbol.iterator] === 'function' && typeof item !== 'string' && !(typeof item.isA === 'function'));
    if (!isSequence) {
      if (depth < shape.length) throw new Error('ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape');
      data.push(item);
      return;
    }
    const items = item instanceof NDArray ? (item.ndim ? [...item] : [item.item()]) : Array.from(item as Iterable<unknown>);
    if (depth === shape.length) shape.push(items.length);
    else if (shape[depth] !== items.length) throw new Error('ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape');
    items.forEach(child => walk(child, depth + 1));
  };
  walk(value, 0);
  const inferred: DType = type ?? (data.every(v => typeof v === 'boolean') && data.length ? 'bool'
    : data.every(v => typeof v === 'number' || typeof v === 'boolean') ? (data.every(v => Number.isInteger(v) && typeof v === 'number') && !(value instanceof Float64Array || value instanceof Float32Array) && data.length ? 'int64' : 'float64')
    : 'object');
  return new NDArray(data.map(v => cast(v, inferred)), shape, undefined, 0, inferred);
}

export function asarray(value: ArrayLike, ...values: unknown[]): NDArray {
  if (value instanceof NDArray && !values.length) return value;
  return array(value, ...values, { copy: false });
}

function shapeOf(shape: number | Iterable<number>): number[] {
  return typeof shape === 'number' ? [shape] : Array.from(shape);
}

export function full(shape: number | Iterable<number>, value: any, ...values: unknown[]): NDArray {
  const { dtype } = { ...options(values), ...(values.length ? { dtype: values[0] } : {}) } as Options;
  const dims = shapeOf(shape);
  const type = dtypeName(dtype) ?? (typeof value === 'boolean' ? 'bool' : 'float64');
  return new NDArray(new Array(product(dims)).fill(cast(value, type)), dims, undefined, 0, type);
}

export const zeros = (shape: number | Iterable<number>, ...values: unknown[]) => full(shape, 0, ...values);
export const ones = (shape: number | Iterable<number>, ...values: unknown[]) => full(shape, 1, ...values);

export function eye(n: number, ...values: unknown[]): NDArray {
  const { M } = options(values);
  const columns = (values[0] as number | undefined) ?? M ?? n;
  const result = zeros([n, columns]);
  for (let i = 0; i < Math.min(n, columns); i++) result.data[i * columns + i] = 1;
  return result;
}

/** numpy.frombuffer for the vertex and index buffers of ifcopenshell.geom (typed arrays or bytes). */
export function frombuffer(buffer: ArrayBufferView | ArrayBuffer | number[], ...values: unknown[]): NDArray {
  const { dtype = 'float64' } = { ...options(values), ...(values.length ? { dtype: values[0] } : {}) } as Options;
  const name = typeof dtype === 'string' ? dtype : dtype === int32 || dtype === intc ? 'int32' : dtype === float32 ? 'float32' : 'float64';
  if (Array.isArray(buffer)) return array(buffer, name.startsWith('int') ? 'int64' : 'float64');
  const bytes = buffer instanceof ArrayBuffer ? buffer : buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength);
  const view = name === 'int32' ? new Int32Array(bytes) : name === 'float32' ? new Float32Array(bytes) : name === 'uint32' ? new Uint32Array(bytes) : new Float64Array(bytes as ArrayBuffer);
  return new NDArray(Array.from(view), [view.length], undefined, 0, name.startsWith('int') || name.startsWith('uint') ? 'int64' : 'float64');
}

// Joining and changing arrays.

function stack(arrays: NDArray[]): NDArray {
  const shape = arrays[0]?.shape ?? [];
  return new NDArray(arrays.flatMap(a => a.values()), [arrays.length, ...shape], undefined, 0, arrays[0]?.dtype ?? 'float64');
}

export function concatenate(arrays: Iterable<ArrayLike>, ...values: unknown[]): NDArray {
  const { axis = 0 } = { ...options(values), ...(values.length ? { axis: values[0] } : {}) } as Options;
  const items = Array.from(arrays, a => asarray(a));
  if (axis === null) return concatenate(items.map(a => a.flatten()));
  const ax = axis < 0 ? axis + items[0]!.ndim : axis;
  const moved = items.map(a => moveAxisToFront(a, ax));
  const result = new NDArray(moved.flatMap(a => a.values()), [moved.reduce((n, a) => n + a.shape[0]!, 0), ...moved[0]!.shape.slice(1)], undefined, 0, moved[0]!.dtype);
  return moveAxisFromFront(result, ax).copy();
}

function moveAxisToFront(array: NDArray, axis: number): NDArray {
  const order = [axis, ...array.shape.map((_, i) => i).filter(i => i !== axis)];
  return array.transpose(...order);
}

function moveAxisFromFront(array: NDArray, axis: number): NDArray {
  const order = array.shape.map((_, i) => i).slice(1);
  order.splice(axis, 0, 0);
  return array.transpose(...order);
}

const atLeast2d = (value: ArrayLike) => {
  const a = asarray(value);
  return a.ndim === 0 ? a.reshape([1, 1]) : a.ndim === 1 ? a.reshape([1, a.size]) : a;
};

export const vstack = (arrays: Iterable<ArrayLike>) => concatenate(Array.from(arrays, atLeast2d), 0);
export const hstack = (arrays: Iterable<ArrayLike>) => {
  const items = Array.from(arrays, a => asarray(a));
  return concatenate(items, items[0]!.ndim === 1 ? 0 : 1);
};

export function append(value: ArrayLike, items: ArrayLike, ...values: unknown[]): NDArray {
  const { axis = null } = { ...options(values), ...(values.length ? { axis: values[0] } : {}) } as Options;
  return axis === null ? concatenate([asarray(value).flatten(), asarray(items).flatten()]) : concatenate([value, items], axis);
}

export function deleteIndices(value: ArrayLike, indices: number | Iterable<number>, ...values: unknown[]): NDArray {
  const { axis = null } = { ...options(values), ...(values.length ? { axis: values[0] } : {}) } as Options;
  const a = axis === null ? asarray(value).flatten() : moveAxisToFront(asarray(value), axis);
  const length = a.shape[0]!;
  const removed = new Set((typeof indices === 'number' ? [indices] : Array.from(indices)).map(i => (i < 0 ? i + length : i)));
  const kept = [...a].filter((_, i) => !removed.has(i)).map(row => asarray(row));
  const result = kept.length ? stack(kept) : new NDArray([], [0, ...a.shape.slice(1)]);
  return axis === null ? result : moveAxisFromFront(result, axis).copy();
}
export { deleteIndices as delete };

export function pad(value: ArrayLike, width: number | number[] | number[][], ...values: unknown[]): NDArray {
  const { constant_values: fill = 0, constantValues = fill } = options(values);
  const a = asarray(value);
  const widths = typeof width === 'number' ? a.shape.map(() => [width, width]) : typeof width[0] === 'number' ? a.shape.map(() => width as number[]) : (width as number[][]);
  const shape = a.shape.map((n, i) => n + widths[i]![0]! + widths[i]![1]!);
  const result = full(shape, constantValues);
  result.__setitem__(widths.map(([before], i) => new Slice(before!, before! + a.shape[i]!, null)), a);
  return result;
}

// Element-wise functions.

const elementwise = (f: (a: number) => number) => (value: ArrayLike) => unary(value, f);
export const sin = elementwise(Math.sin);
export const cos = elementwise(Math.cos);
export const arcsin = elementwise(Math.asin);
export const arccos = elementwise(Math.acos);
export const arctan = elementwise(Math.atan);
export const radians = elementwise(v => (v * Math.PI) / 180);

/** Python/numpy rounding: halves to even. */
function roundHalfEven(value: number, decimals: number): number {
  const scale = 10 ** decimals;
  const scaled = value * scale;
  const floor = Math.floor(scaled);
  const fraction = scaled - floor;
  const rounded = Math.abs(fraction - 0.5) < 1e-9 ? (floor % 2 === 0 ? floor : floor + 1) : Math.round(scaled);
  return rounded / scale;
}

export function round(value: ArrayLike, ...values: unknown[]): any {
  const { decimals = 0 } = { ...options(values), ...(values.length ? { decimals: values[0] } : {}) } as Options;
  if (typeof value === 'number') return roundHalfEven(value, decimals);
  const a = asarray(value);
  return new NDArray(a.values().map(v => roundHalfEven(v, decimals)), [...a.shape], undefined, 0, a.dtype);
}

export function clip(value: ArrayLike, lower: number | null, upper: number | null): any {
  return unary(value, v => Math.min(upper ?? Infinity, Math.max(lower ?? -Infinity, v)));
}

const binaryFunction = (f: (a: any, b: any) => any, dtype?: DType) => (a: ArrayLike, b: ArrayLike) => {
  if (typeof a === 'number' && typeof b === 'number') return f(a, b);
  return binary(asarray(a), asarray(b), f, dtype);
};
export const subtract = binaryFunction((a, b) => a - b);
export const divide = binaryFunction((a, b) => a / b, 'float64');
export const arctan2 = binaryFunction(Math.atan2, 'float64');

/** numpy.where(condition, x, y), or the indices of true values for numpy.where(condition). */
export function where(condition: ArrayLike, ...values: ArrayLike[]): any {
  if (!values.length) return nonzero(condition);
  const c = asarray(condition);
  const x = asarray(values[0]!);
  const y = asarray(values[1]!);
  const shape = broadcastShape(broadcastShape(c.shape, x.shape), y.shape);
  const cs = broadcastTo(c, shape).values();
  const xs = broadcastTo(x, shape).values();
  const ys = broadcastTo(y, shape).values();
  const result = new NDArray(cs.map((v, i) => (v ? xs[i] : ys[i])), shape, undefined, 0, resultType(x, y));
  return shape.length ? result : result.data[0];
}

/** Indices of non-zero values, one index array per dimension. */
export function nonzero(value: ArrayLike): NDArray[] {
  const a = asarray(value);
  const result: number[][] = a.shape.map(() => []);
  const strides = contiguous(a.shape);
  a.values().forEach((v, flat) => {
    if (!v) return;
    strides.forEach((stride, axis) => result[axis]!.push(Math.floor(flat / stride) % a.shape[axis]!));
  });
  return result.map(indices => new NDArray(indices, [indices.length], undefined, 0, 'int64'));
}

// Reductions.

function reduce(value: ArrayLike, values: unknown[], f: (items: any[]) => any, dtype?: DType): any {
  const { axis = null } = { ...options(values), ...(values.length ? { axis: values[0] } : {}) } as Options;
  const a = asarray(value);
  if (axis === null || a.ndim <= 1) return f(a.values());
  const ax = axis < 0 ? axis + a.ndim : axis;
  const moved = moveAxisFromFront(moveAxisToFront(a, ax), a.ndim - 1);
  const outer = moved.shape.slice(0, -1);
  const rows = moved.reshape([product(outer), moved.shape[moved.ndim - 1]!]);
  const data = [...rows].map(row => f((row as NDArray).values()));
  return new NDArray(data, outer, undefined, 0, dtype ?? (data.every(Number.isInteger) && a.dtype !== 'float64' ? 'int64' : 'float64'));
}

export const sum = (value: ArrayLike, ...values: unknown[]) => reduce(value, values, items => items.reduce((a, b) => a + Number(b), 0));
export const mean = (value: ArrayLike, ...values: unknown[]) => reduce(value, values, items => items.reduce((a, b) => a + b, 0) / items.length, 'float64');
export const min = (value: ArrayLike, ...values: unknown[]) => reduce(value, values, items => {
  if (!items.length) throw new Error('ValueError: zero-size array to reduction operation minimum which has no identity');
  return items.reduce((a, b) => (b < a || Number.isNaN(b) ? b : a));
});
export const max = (value: ArrayLike, ...values: unknown[]) => reduce(value, values, items => {
  if (!items.length) throw new Error('ValueError: zero-size array to reduction operation maximum which has no identity');
  return items.reduce((a, b) => (b > a || Number.isNaN(b) ? b : a));
});
export const any = (value: ArrayLike, ...values: unknown[]) => reduce(value, values, items => items.some(Boolean), 'bool');
export const all = (value: ArrayLike, ...values: unknown[]) => reduce(value, values, items => items.every(Boolean), 'bool');

export function argmax(value: ArrayLike): number {
  const items = asarray(value).values();
  return items.reduce((best, v, i) => (v > items[best] ? i : best), 0);
}

export function argmin(value: ArrayLike): number {
  const items = asarray(value).values();
  return items.reduce((best, v, i) => (v < items[best] ? i : best), 0);
}

export function isclose(a: ArrayLike, b: ArrayLike, ...values: unknown[]): any {
  const { rtol = 1e-5, atol = 1e-8 } = { ...options(values), ...(values.length ? { rtol: values[0], atol: values[1] ?? 1e-8 } : {}) } as Options;
  const close = (x: number, y: number) => x === y || Math.abs(x - y) <= atol + rtol * Math.abs(y);
  if (typeof a === 'number' && typeof b === 'number') return close(a, b);
  return binary(asarray(a), asarray(b), close, 'bool');
}

export function allclose(a: ArrayLike, b: ArrayLike, ...values: unknown[]): boolean {
  const result = isclose(a, b, ...values);
  return result instanceof NDArray ? result.values().every(Boolean) : Boolean(result);
}

// Linear algebra.

/** numpy.dot: inner product of vectors, matrix products, or scaling by a number. */
export function dot(a: ArrayLike, b: ArrayLike): any {
  const x = asarray(a);
  const y = asarray(b);
  if (!x.ndim || !y.ndim) return binary(x, y, (p, q) => p * q);
  return matmul(x, y);
}

export function matmul(a: ArrayLike, b: ArrayLike): any {
  const x = asarray(a);
  const y = asarray(b);
  const left = x.ndim === 1 ? x.reshape([1, x.size]) : x;
  const right = y.ndim === 1 ? y.reshape([y.size, 1]) : y;
  if (left.ndim !== 2 || right.ndim !== 2) throw new Error('matmul: only 1-D and 2-D arrays are supported');
  const [n, k] = left.shape as [number, number];
  const [k2, m] = right.shape as [number, number];
  if (k !== k2) throw new Error(`ValueError: matmul: Input operand 1 has a mismatch in its core dimension 0 (size ${k2} is different from ${k})`);
  const l = left.values();
  const r = right.values();
  const data = new Array<number>(n * m).fill(0);
  for (let i = 0; i < n; i++) for (let j = 0; j < m; j++) {
    let total = 0;
    for (let q = 0; q < k; q++) total += l[i * k + q] * r[q * m + j];
    data[i * m + j] = total;
  }
  const shape = [...(x.ndim === 1 ? [] : [n]), ...(y.ndim === 1 ? [] : [m])];
  return shape.length ? new NDArray(data, shape, undefined, 0, resultType(x, y)) : data[0];
}

/** numpy.cross of 3-D vectors, or the scalar z component for 2-D vectors; rows of 2-D arrays are crossed. */
export function cross(a: ArrayLike, b: ArrayLike): any {
  const x = asarray(a);
  const y = asarray(b);
  if (x.ndim > 1 || y.ndim > 1) {
    const rows = broadcastShape(x.shape.slice(0, -1), y.shape.slice(0, -1));
    const xs = broadcastTo(x, [...rows, x.shape[x.ndim - 1]!]);
    const ys = broadcastTo(y, [...rows, y.shape[y.ndim - 1]!]);
    return stack([...xs].map((row, i) => asarray(cross(row as NDArray, ys.__getitem__(i)))));
  }
  const [a0 = 0, a1 = 0, a2 = 0] = x.values();
  const [b0 = 0, b1 = 0, b2 = 0] = y.values();
  if (x.size === 2 && y.size === 2) return a0 * b1 - a1 * b0;
  return new NDArray([a1 * b2 - a2 * b1, a2 * b0 - a0 * b2, a0 * b1 - a1 * b0], [3]);
}

export function outer(a: ArrayLike, b: ArrayLike): NDArray {
  const x = asarray(a).values();
  const y = asarray(b).values();
  return new NDArray(x.flatMap(p => y.map(q => p * q)), [x.length, y.length]);
}

/** Gauss-Jordan elimination with partial pivoting; a singular matrix raises LinAlgError. */
function inv(value: ArrayLike): NDArray {
  const a = asarray(value);
  const n = a.shape[0]!;
  if (a.ndim !== 2 || a.shape[1] !== n) throw new Error('LinAlgError: Last 2 dimensions of the array must be square');
  const m = [...a].map(row => [...(row as NDArray).values(), ...Array.from({ length: n }, (_, j) => 0)]);
  m.forEach((row, i) => (row[n + i] = 1));
  for (let col = 0; col < n; col++) {
    let pivot = col;
    for (let r = col + 1; r < n; r++) if (Math.abs(m[r]![col]!) > Math.abs(m[pivot]![col]!)) pivot = r;
    if (Math.abs(m[pivot]![col]!) < 1e-300) throw new Error('LinAlgError: Singular matrix');
    [m[col], m[pivot]] = [m[pivot]!, m[col]!];
    const p = m[col]![col]!;
    m[col] = m[col]!.map(v => v / p);
    for (let r = 0; r < n; r++) {
      if (r === col) continue;
      const factor = m[r]![col]!;
      if (factor) m[r] = m[r]!.map((v, j) => v - factor * m[col]![j]!);
    }
  }
  return new NDArray(m.flatMap(row => row.slice(n)), [n, n]);
}

/** Euclidean (Frobenius) norm, optionally along an axis. */
function norm(value: ArrayLike, ...values: unknown[]): any {
  if (typeof value === 'number') return Math.abs(value);
  return reduce(value, values, items => Math.sqrt(items.reduce((a, b) => a + b * b, 0)), 'float64');
}

export const linalg = { norm, inv };

// Scalar types and constants, as numpy names them.

export const float64 = (value: unknown = 0) => Number(value);
export const float32 = float64;
export const int64 = (value: unknown = 0) => Math.trunc(Number(value));
export const int32 = int64;
export const intc = int64;
export const bool_ = (value: unknown = false) => Boolean(value);
export const ndarray = NDArray;
export const pi = Math.PI;
export const e = Math.E;
export const inf = Infinity;
export const nan = NaN;
export const newaxis = null;

// Code that indexes nested lists as arrays (see _py.ts getitem) gets them converted.
hooks.asarray = value => asarray(value as ArrayLike);
