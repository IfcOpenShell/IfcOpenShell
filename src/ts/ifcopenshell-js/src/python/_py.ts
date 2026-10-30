// This file was generated with the assistance of an AI coding tool.
// SPDX-License-Identifier: LGPL-3.0-or-later

// Python semantics for generated code, used only where a value's type is not known when
// transpiling. Hand-written, unlike the transpiled util/ and api/ next to it.

import { readResource } from "../file.js";

function isDict(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && Object.getPrototypeOf(value) === Object.prototype;
}

/** A Python special method (`__len__`, `__add__`, ...) of a runtime object, such as an array or a date. */
function dunder(value: unknown, name: string): ((...args: unknown[]) => unknown) | undefined {
  const method = value !== null && typeof value === 'object' ? (value as Record<string, unknown>)[name] : undefined;
  return typeof method === 'function' ? (method as (...args: unknown[]) => unknown).bind(value) : undefined;
}

/** Python truthiness: empty strings, lists, sets and dicts are false. */
export function truthy(value: unknown): boolean {
  if (Array.isArray(value) || typeof value === 'string') return value.length > 0;
  if (value instanceof Set || value instanceof Map) return value.size > 0;
  if (isDict(value)) return Object.keys(value).length > 0;
  const bool = dunder(value, '__bool__') ?? dunder(value, '__len__');
  if (bool) return Boolean(bool());
  return Boolean(value);
}

/** Python `len()`. */
export function len(value: unknown): number {
  if (Array.isArray(value) || typeof value === 'string') return value.length;
  if (value instanceof Set || value instanceof Map) return value.size;
  if (isDict(value)) return Object.keys(value).length;
  const length = dunder(value, '__len__');
  if (length) return length() as number;
  // An entity's length is its number of forward attributes.
  if (value !== null && typeof (value as { attributes?: unknown }).attributes === 'function') {
    return (value as { attributes(): unknown[] }).attributes().length;
  }
  throw new TypeError(`object of type ${typeof value} has no len()`);
}

/** Python `item in container`. */
export function contains(container: unknown, item: unknown): boolean {
  if (typeof container === 'string') return container.includes(item as string);
  if (Array.isArray(container)) return container.includes(item);
  if (container instanceof Set || container instanceof Map) return container.has(item);
  if (isDict(container)) return Object.hasOwn(container, item as string);
  const contains = dunder(container, '__contains__');
  if (contains) return Boolean(contains(item));
  throw new TypeError(`argument of type ${typeof container} is not iterable`);
}

/** Python `container.remove(item)` for lists, sets and files. */
export function remove(container: unknown, item: unknown): void {
  if (Array.isArray(container)) {
    const index = container.indexOf(item);
    if (index < 0) throw new Error('list.remove(x): x not in list');
    container.splice(index, 1);
  } else if (container instanceof Set) {
    if (!container.delete(item)) throw new Error('set.remove(x): x not in set');
  } else if (container !== null && typeof (container as { remove?: unknown }).remove === 'function') {
    (container as { remove(item: unknown): void }).remove(item);
  } else {
    throw new TypeError(`cannot remove from ${typeof container}`);
  }
}

/** Python `container.pop()` without arguments: the last list item, or any set member. */
export function pop(container: unknown): unknown {
  if (Array.isArray(container)) {
    if (!container.length) throw new Error('pop from empty list');
    return container.pop();
  }
  if (container instanceof Set) {
    const iterator = container.values().next();
    if (iterator.done) throw new Error('pop from an empty set');
    container.delete(iterator.value);
    return iterator.value;
  }
  throw new TypeError(`cannot pop from ${typeof container}`);
}

/** Python ordering: numbers, strings, booleans, and lists or tuples compared item by item. */
export function compare(a: unknown, b: unknown): number {
  if (Array.isArray(a) && Array.isArray(b)) {
    for (let i = 0; i < Math.min(a.length, b.length); i++) {
      const order = compare(a[i], b[i]);
      if (order) return order;
    }
    return a.length - b.length;
  }
  if (typeof a !== typeof b && !(typeof a === 'boolean' || typeof b === 'boolean')) {
    throw new TypeError(`'<' not supported between instances of '${typeof a}' and '${typeof b}'`);
  }
  return (a as number) < (b as number) ? -1 : (a as number) > (b as number) ? 1 : 0;
}

/** Python `min(values, key=..., default=...)`: the first smallest item, compared with Python ordering. */
export function min<T>(values: Iterable<T>, options: { key?: ((value: T) => unknown) | null; default?: T } = {}): T {
  return extreme(values, options, -1, 'min');
}

/** Python `max(values, key=..., default=...)`. */
export function max<T>(values: Iterable<T>, options: { key?: ((value: T) => unknown) | null; default?: T } = {}): T {
  return extreme(values, options, 1, 'max');
}

function extreme<T>(values: Iterable<T>, options: { key?: ((value: T) => unknown) | null; default?: T }, sign: number, name: string): T {
  const key = options.key ?? ((value: T) => value);
  let best: T | undefined;
  let bestKey: unknown;
  let found = false;
  for (const value of values) {
    const k = key(value);
    if (!found || order(k, bestKey) * sign > 0) {
      best = value;
      bestKey = k;
      found = true;
    }
  }
  if (found) return best as T;
  if ('default' in options) return options.default as T;
  throw new Error(`ValueError: ${name}() iterable argument is empty`);
}

/** Python ordering, including objects such as dates that order by valueOf(). */
function order(a: unknown, b: unknown): number {
  if (typeof a === 'object' && a !== null && !Array.isArray(a)) return (a as unknown as number) < (b as unknown as number) ? -1 : (a as unknown as number) > (b as unknown as number) ? 1 : 0;
  return compare(a, b);
}

/** Python `sorted(values, key=..., reverse=...)`; stable, like Python. */
export function sorted<T>(values: Iterable<T>, options: { key?: ((value: T) => unknown) | null; reverse?: boolean } = {}): T[] {
  const key = options.key ?? ((value: T) => value);
  const items = Array.from(values, value => [key(value), value] as const);
  items.sort((a, b) => (options.reverse ? -1 : 1) * compare(a[0], b[0]));
  return items.map(([, value]) => value);
}

/** Python `list.sort(key=..., reverse=...)`, in place. */
export function sort<T>(values: T[], options: { key?: ((value: T) => unknown) | null; reverse?: boolean } = {}): void {
  const result = sorted(values, options);
  values.splice(0, values.length, ...result);
}

/** Python `round()`: halves round to even. */
export function round(value: number, digits?: number | null): number {
  const scale = 10 ** (digits ?? 0);
  const scaled = value * scale;
  const floor = Math.floor(scaled);
  const fraction = scaled - floor;
  const rounded = Math.abs(fraction - 0.5) < 1e-9 ? (floor % 2 === 0 ? floor : floor + 1) : Math.round(scaled);
  return digits === undefined || digits === null ? rounded : rounded / scale;
}

/** Python `str.partition(separator)`. */
export function partition(text: string, separator: string): [string, string, string] {
  const index = text.indexOf(separator);
  return index < 0 ? [text, '', ''] : [text.slice(0, index), separator, text.slice(index + separator.length)];
}

/** Python `str.rpartition(separator)`. */
export function rpartition(text: string, separator: string): [string, string, string] {
  const index = text.lastIndexOf(separator);
  return index < 0 ? ['', '', text] : [text.slice(0, index), separator, text.slice(index + separator.length)];
}

/** Python `dict(values)` from pairs or a mapping: a plain object for string keys, else a PyDict. */
export function dict(values: unknown): any {
  if (values instanceof Map) return new PyDict(values);
  if (isDict(values)) return { ...values };
  const pairs = Array.from(values as Iterable<[unknown, unknown]>, pair => Array.from(pair) as [unknown, unknown]);
  return pairs.every(([key]) => typeof key === 'string') ? Object.fromEntries(pairs) : new PyDict(pairs);
}

/** Options object for `f(a, *values)`: values fill the optional parameters `names` in order. */
export function positionalOptions(names: string[], values: Iterable<unknown>): Record<string, unknown> {
  const items = Array.from(values);
  if (items.length > names.length) throw new TypeError(`takes at most ${names.length} optional arguments (${items.length} given)`);
  return Object.fromEntries(items.map((value, i) => [names[i], value]));
}

/** Python `range(start, stop, step)` as an array. */
export function range(start: number, stop: number, step = 1): number[] {
  if (step === 0) throw new Error('ValueError: range() arg 3 must not be zero');
  const result: number[] = [];
  for (let i = start; step > 0 ? i < stop : i > stop; i += step) result.push(i);
  return result;
}

/** Python `str.isdigit()` and the other character class tests: false for empty strings. */
export const str = {
  isdigit: (text: string) => /^\d+$/.test(text),
  isdecimal: (text: string) => /^\d+$/.test(text),
  isnumeric: (text: string) => /^\p{N}+$/u.test(text),
  isalpha: (text: string) => /^\p{L}+$/u.test(text),
  isalnum: (text: string) => /^[\p{L}\p{N}]+$/u.test(text),
  isspace: (text: string) => /^\s+$/.test(text),
  isupper: (text: string) => /\p{Lu}/u.test(text) && text === text.toUpperCase(),
  islower: (text: string) => /\p{Ll}/u.test(text) && text === text.toLowerCase(),
};

/** Python `format(value, spec)`: [[fill]align][sign][#][0][width][,|_][.precision][type]. */
export function formatValue(value: unknown, spec: string): string {
  const match = /^(?:(.)?([<>=^]))?([+\- ])?(#)?(0)?(\d+)?([,_])?(?:\.(\d+))?([bcdeEfFgGnosxX%])?$/s.exec(spec);
  if (!match) throw new Error(`ValueError: Invalid format specifier '${spec}'`);
  const [, fillChar, alignChar, sign = '-', , zero, widthText, grouping, precisionText, type] = match;
  const precision = precisionText === undefined ? undefined : Number(precisionText);
  let text: string;
  let negative = false;
  if (typeof value === 'number' || typeof value === 'boolean') {
    let number = Number(value);
    // Python integers have no negative zero (JS turns -1 * 0 into -0).
    negative = number < 0 || (Object.is(number, -0) && type !== 'd' && type !== 'n');
    number = Math.abs(number);
    switch (type) {
      case 'd': case 'n':
        if (!Number.isInteger(number)) throw new Error("ValueError: Unknown format code 'd' for object of type 'float'");
        text = String(number);
        break;
      case 'f': case 'F': text = number.toFixed(precision ?? 6); break;
      case 'e': case 'E': text = number.toExponential(precision ?? 6).replace(/e([+-])(\d)$/, 'e$10$2'); break;
      case '%': text = `${(number * 100).toFixed(precision ?? 6)}%`; break;
      case 'x': case 'X': text = number.toString(16); break;
      case 'o': text = number.toString(8); break;
      case 'b': text = number.toString(2); break;
      case 'g': case 'G': {
        const p = precision === 0 ? 1 : precision ?? 6;
        const exponent = number === 0 ? 0 : Math.floor(Math.log10(number));
        text = exponent < -4 || exponent >= p
          ? number.toExponential(p - 1).replace(/\.?0+e/, 'e').replace(/e([+-])(\d)$/, 'e$10$2')
          : number.toFixed(Math.max(0, p - 1 - exponent)).replace(/\.?0+$/, '');
        break;
      }
      default:
        text = precision === undefined ? (Number.isInteger(number) && typeof value === 'number' && !type ? String(number) : String(number)) : number.toPrecision(precision);
    }
    if (type && 'EFGX'.includes(type)) text = text.toUpperCase();
    if (grouping) {
      const [whole, fraction] = text.split('.');
      text = whole!.replace(/\B(?=(\d{3})+(?!\d))/g, grouping) + (fraction !== undefined ? `.${fraction}` : '');
    }
  } else {
    text = String(value ?? 'None');
    if (precision !== undefined) text = text.slice(0, precision);
  }
  const signText = negative ? '-' : sign === '+' ? '+' : sign === ' ' ? ' ' : '';
  const width = Number(widthText ?? 0);
  const numeric = typeof value === 'number' || typeof value === 'boolean';
  const align = alignChar ?? (zero && numeric ? '=' : numeric ? '>' : '<');
  const fill = fillChar ?? (zero && !alignChar ? '0' : ' ');
  const padding = Math.max(0, width - signText.length - text.length);
  if (align === '=') return signText + fill.repeat(padding) + text;
  const body = signText + text;
  if (align === '<') return body + fill.repeat(padding);
  if (align === '^') return fill.repeat(Math.floor(padding / 2)) + body + fill.repeat(Math.ceil(padding / 2));
  return fill.repeat(padding) + body;
}

/** Python `template.format(*args, **kwargs)`; keyword arguments are a trailing object. */
export function format(template: string, ...args: unknown[]): string {
  const last = args[args.length - 1];
  const keywords = isDict(last) ? (args.pop() as Record<string, unknown>) : {};
  let next = 0;
  const field = (name: string): unknown => {
    const [, head = '', rest = ''] = /^([^.[]*)(.*)$/.exec(name)!;
    let value = head === '' ? args[next++] : /^\d+$/.test(head) ? args[Number(head)] : keywords[head];
    for (const [, attribute, key] of rest.matchAll(/\.(\w+)|\[([^\]]+)\]/g)) {
      value = attribute !== undefined ? (value as Record<string, unknown>)[attribute] : (value as Record<string, unknown>)[key!];
    }
    return value;
  };
  const replace = (text: string): string => text.replace(/\{\{|\}\}|\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}/g, (whole, body?: string) => {
    if (whole === '{{') return '{';
    if (whole === '}}') return '}';
    const [, name = '', conversion, spec = ''] = /^([^!:]*)(?:!([rsa]))?(?::(.*))?$/s.exec(body!)!;
    let value = field(name);
    if (conversion === 'r') value = typeof value === 'string' ? `'${value}'` : String(value);
    else if (conversion) value = String(value);
    return formatValue(value, replace(spec));
  });
  return replace(template);
}

/** Python regular expressions as JS RegExp: named groups and Python flags translated. */
function regexp(pattern: string | RegExp, flags = 0, extra = ''): RegExp {
  if (pattern instanceof RegExp) return new RegExp(pattern.source, pattern.flags.replace(/[gy]/g, '') + extra);
  const source = pattern.replace(/\(\?P</g, '(?<').replace(/\(\?P=(\w+)\)/g, '\\k<$1>');
  return new RegExp(source, (flags & 2 ? 'i' : '') + (flags & 8 ? 'm' : '') + (flags & 16 ? 's' : '') + extra);
}

/** Python `re.Match`. */
export class Match {
  constructor(private readonly result: RegExpExecArray) {}
  group(index: number | string = 0): string | null {
    const value = typeof index === 'number' ? this.result[index] : this.result.groups?.[index];
    return value ?? null;
  }
  groups(): (string | null)[] {
    return this.result.slice(1).map(value => value ?? null);
  }
  start(): number {
    return this.result.index;
  }
  end(): number {
    return this.result.index + this.result[0].length;
  }
}

/** Python `re` functions used by ifcopenshell. Flags use Python's values (re.I is 2). */
export const re = {
  I: 2, IGNORECASE: 2, M: 8, MULTILINE: 8, S: 16, DOTALL: 16,
  match(pattern: string | RegExp, text: string, flags = 0): Match | null {
    const result = regexp(pattern, flags, 'y').exec(text);
    return result ? new Match(result) : null;
  },
  fullmatch(pattern: string | RegExp, text: string, flags = 0): Match | null {
    const source = pattern instanceof RegExp ? pattern.source : pattern;
    const result = regexp(`(?:${source})$`, flags, 'y').exec(text);
    return result ? new Match(result) : null;
  },
  search(pattern: string | RegExp, text: string, flags = 0): Match | null {
    const result = regexp(pattern, flags).exec(text);
    return result ? new Match(result) : null;
  },
  findall(pattern: string | RegExp, text: string, flags = 0): (string | string[])[] {
    return [...text.matchAll(regexp(pattern, flags, 'g'))].map(m => (m.length > 2 ? m.slice(1) : m[m.length > 1 ? 1 : 0]!) as string | string[]);
  },
  sub(pattern: string | RegExp, replacement: string | ((match: Match) => string), text: string, count = 0, flags = 0): string {
    let remaining = count || Infinity;
    return text.replace(regexp(pattern, flags, 'g'), (...args) => {
      const whole = args[0] as string;
      if (remaining-- <= 0) return whole;
      if (typeof replacement === 'function') {
        const offset = args.findIndex(a => typeof a === 'number');
        const result = Object.assign([...args.slice(0, offset)], { index: args[offset], input: text }) as unknown as RegExpExecArray;
        return replacement(new Match(result));
      }
      return replacement.replace(/\\(\d+)|\\g<(\w+)>/g, (_, n, name) => (name ? (args.at(-1) as Record<string, string>)?.[name] : args[Number(n)]) ?? '');
    });
  },
  split(pattern: string | RegExp, text: string, flags = 0): string[] {
    return text.split(regexp(pattern, flags));
  },
  compile(pattern: string, flags = 0) {
    const self = re;
    return {
      pattern,
      match: (text: string) => self.match(pattern, text, flags),
      fullmatch: (text: string) => self.fullmatch(pattern, text, flags),
      search: (text: string) => self.search(pattern, text, flags),
      findall: (text: string) => self.findall(pattern, text, flags),
      sub: (replacement: string | ((match: Match) => string), text: string, count = 0) => self.sub(pattern, replacement, text, count, flags),
      split: (text: string) => self.split(pattern, text, flags),
    };
  },
  escape(text: string): string {
    return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  },
};

/** Python `pathlib.Path` for locating files next to a module; paths are file URLs or plain paths. */
export class Path {
  constructor(readonly path: string) {}
  get parent(): Path {
    return new Path(this.path.replace(/[\\/][^\\/]*[\\/]?$/, '') || '/');
  }
  absolute(): Path {
    return this;
  }
  resolve(): Path {
    return this;
  }
  joinpath(...parts: string[]): Path {
    return new Path([this.path.replace(/[\\/]$/, ''), ...parts].join('/'));
  }
  get name(): string {
    return this.path.split(/[\\/]/).pop() ?? '';
  }
  toString(): string {
    return this.path;
  }
}

/** Python `zip(...)`: tuples up to the shortest input. */
export function zip(...iterables: Iterable<unknown>[]): unknown[][] {
  const arrays = iterables.map(values => Array.from(values));
  const length = arrays.length ? Math.min(...arrays.map(values => values.length)) : 0;
  return Array.from({ length }, (_, i) => arrays.map(values => values[i]));
}

/** Python `iter(values)`. */
export function iter<T>(values: Iterable<T>): Iterator<T> {
  return values[Symbol.iterator]();
}

/** Python `next(iterator)` on an iterator, or the first item of an iterable; StopIteration when exhausted. */
export function next<T>(values: Iterator<T> | Iterable<T>, ...otherwise: [T?]): T {
  const iterator = typeof (values as Iterator<T>).next === 'function' ? values as Iterator<T> : iter(values as Iterable<T>);
  const result = iterator.next();
  if (!result.done) return result.value;
  if (otherwise.length) return otherwise[0] as T;
  throw new Error('StopIteration');
}

/** Python `dataclasses.asdict(instance)`: own fields, recursing into dataclasses, lists and dicts. */
export function asdict(value: unknown): Record<string, unknown> {
  const convert = (item: unknown): unknown => {
    if (Array.isArray(item)) return item.map(convert);
    if (isDict(item)) return Object.fromEntries(Object.entries(item).map(([k, v]) => [k, convert(v)]));
    if (item !== null && typeof item === 'object' && typeof (item.constructor as { fromKwargs?: unknown }).fromKwargs === 'function') return asdict(item);
    return item;
  };
  return Object.fromEntries(Object.entries(value as object).map(([k, v]) => [k, convert(v)]));
}

/** Python `x.copy()` of a list, dict, set or object with a `copy` method. */
export function copy<T>(value: T): T {
  if (Array.isArray(value)) return [...value] as T;
  if (value instanceof PyDict) return new PyDict(value) as T;
  if (value instanceof Map) return new Map(value) as T;
  if (value instanceof Set) return new Set(value) as T;
  if (isDict(value)) return { ...value };
  const method = dunder(value, 'copy');
  if (method) return method() as T;
  throw new TypeError(`cannot copy ${typeof value}`);
}

/**
 * Python binary operators. Numbers and strings use JS operators; lists follow Python list
 * semantics; other objects (arrays, dates) implement `__add__`/`__radd__` and so on.
 */
function binary(name: string, a: any, b: any, numbers: (a: any, b: any) => any): any {
  if (typeof a === 'number' && typeof b === 'number') return numbers(a, b);
  const forward = dunder(a, `__${name}__`);
  if (forward) {
    const result = forward(b);
    if (result !== NotImplemented) return result;
  }
  const reflected = dunder(b, `__r${name}__`);
  if (reflected) {
    const result = reflected(a);
    if (result !== NotImplemented) return result;
  }
  if (typeof a === 'boolean' || typeof b === 'boolean' || typeof a === 'string' && typeof b === 'string') return numbers(a, b);
  // A list with a numpy scalar (which JS numbers stand for), as in `[1, 2] / np.linalg.norm(v)`.
  if (hooks.asarray && name !== 'add' && name !== 'mul' && (Array.isArray(a) || Array.isArray(b))) {
    return binary(name, Array.isArray(a) ? hooks.asarray(a) : a, Array.isArray(b) ? hooks.asarray(b) : b, numbers);
  }
  throw new TypeError(`unsupported operand type(s) for ${name}: '${typeName(a)}' and '${typeName(b)}'`);
}

/** Returned by special methods that do not support an operand, as Python's NotImplemented. */
export const NotImplemented: unique symbol = Symbol('NotImplemented');

function typeName(value: unknown): string {
  if (value === null || value === undefined) return 'NoneType';
  if (Array.isArray(value)) return 'list';
  return typeof value === 'object' ? (value as object).constructor.name : typeof value;
}

/** Python `a + b`: lists and tuples concatenate. */
export function add(a: any, b: any): any {
  if (Array.isArray(a) && Array.isArray(b)) return [...a, ...b];
  return binary('add', a, b, (x, y) => x + y);
}

export function sub(a: any, b: any): any {
  return binary('sub', a, b, (x, y) => x - y);
}

/** Python `a * b`: a list times an integer repeats it. */
export function mul(a: any, b: any): any {
  if (Array.isArray(a) && Number.isInteger(b)) return Array.from({ length: Math.max(0, b) }, () => a).flat();
  if (Array.isArray(b) && Number.isInteger(a)) return mul(b, a);
  if (typeof a === 'string' && Number.isInteger(b)) return a.repeat(Math.max(0, b));
  return binary('mul', a, b, (x, y) => x * y);
}

export function truediv(a: any, b: any): any {
  return binary('truediv', a, b, (x, y) => {
    if (y === 0) throw new Error('ZeroDivisionError: division by zero');
    return x / y;
  });
}

/** Python `a // b`: rounds towards negative infinity. */
export function floordiv(a: any, b: any): any {
  return binary('floordiv', a, b, (x, y) => {
    if (y === 0) throw new Error('ZeroDivisionError: integer division or modulo by zero');
    return Math.floor(x / y);
  });
}

/** Python `a % b`: the result has the sign of the divisor. */
export function mod(a: any, b: any): any {
  return binary('mod', a, b, (x, y) => {
    if (y === 0) throw new Error('ZeroDivisionError: integer division or modulo by zero');
    return ((x % y) + y) % y;
  });
}

export function pow(a: any, b: any): any {
  return binary('pow', a, b, (x, y) => x ** y);
}

export function matmul(a: any, b: any): any {
  return binary('matmul', a, b, () => {
    throw new TypeError("unsupported operand type(s) for @: 'float' and 'float'");
  });
}

/** In-place operators: `__iadd__` and so on when the object has them, else the binary operator. */
function inplace(name: string, a: any, b: any, operator: (a: any, b: any) => any): any {
  const method = dunder(a, `__i${name}__`);
  if (method) {
    const result = method(b);
    if (result !== NotImplemented) return result;
  }
  return operator(a, b);
}

/** Python `a += b`: lists are extended in place. */
export function iadd(a: any, b: any): any {
  if (Array.isArray(a)) {
    a.push(...b);
    return a;
  }
  return inplace('add', a, b, add);
}

export const isub = (a: any, b: any): any => inplace('sub', a, b, sub);
export const imul = (a: any, b: any): any => inplace('mul', a, b, mul);
export const itruediv = (a: any, b: any): any => inplace('truediv', a, b, truediv);
export const ifloordiv = (a: any, b: any): any => inplace('floordiv', a, b, floordiv);
export const imod = (a: any, b: any): any => inplace('mod', a, b, mod);
export const ipow = (a: any, b: any): any => inplace('pow', a, b, pow);
export const imatmul = (a: any, b: any): any => inplace('matmul', a, b, matmul);

/** Python `-a`. */
export function neg(a: any): any {
  if (typeof a === 'number') return -a;
  const method = dunder(a, '__neg__');
  if (method) return method();
  throw new TypeError(`bad operand type for unary -: '${typeName(a)}'`);
}

/** Python `a == b`: `__eq__` when defined, lists and tuples by value, otherwise identity. */
export function eq(a: any, b: any): boolean {
  const method = dunder(a, '__eq__') ?? dunder(b, '__eq__');
  // Arrays compare element-wise, as numpy does; other objects give a boolean.
  if (method) return (dunder(a, '__eq__') ? method(b) : method(a)) as boolean;
  if (Array.isArray(a) && Array.isArray(b)) return a.length === b.length && a.every((value, i) => eq(value, b[i]));
  return a === b || (a === null && b === undefined) || (a === undefined && b === null);
}

/** Python `slice(start, stop, step)`. */
export class Slice {
  constructor(readonly start: number | null, readonly stop: number | null, readonly step: number | null) {}

  /** Python `slice.indices(length)`: concrete start, stop and step for a sequence of this length. */
  indices(length: number): [number, number, number] {
    const step = this.step ?? 1;
    if (step === 0) throw new Error('ValueError: slice step cannot be zero');
    const clamp = (value: number | null, otherwise: number, lower: number, upper: number) => {
      if (value === null) return otherwise;
      const index = value < 0 ? value + length : value;
      return Math.min(Math.max(index, lower), upper);
    };
    return step > 0
      ? [clamp(this.start, 0, 0, length), clamp(this.stop, length, 0, length), step]
      : [clamp(this.start, length - 1, -1, length - 1), clamp(this.stop, -1, -1, length - 1), step];
  }

  /** Indices selected from a sequence of this length. */
  range(length: number): number[] {
    const [start, stop, step] = this.indices(length);
    const result: number[] = [];
    for (let i = start; step > 0 ? i < stop : i > stop; i += step) result.push(i);
    return result;
  }
}

export function slice(start: number | null, stop?: number | null, step?: number | null): Slice {
  // slice(stop) has a single argument.
  return stop === undefined ? new Slice(null, start, null) : new Slice(start, stop, step ?? null);
}

function sequenceIndex(length: number, index: number): number {
  const position = index < 0 ? index + length : index;
  if (!Number.isInteger(position) || position < 0 || position >= length) throw new Error('IndexError: index out of range');
  return position;
}

/** A list used as an index, as Python `a[[0, 2]]`, as opposed to a tuple of indices `a[0, 2]`. */
export class IndexList {
  constructor(readonly items: unknown[]) {}
}

/** Set by the numpy runtime: Python code receiving nested lists where it expects arrays indexes them as arrays. */
export const hooks: { asarray: ((value: unknown) => unknown) | null } = { asarray: null };

/** Python `container[key]`, with negative indices, slices and `__getitem__`. */
export function getitem(container: any, key: any): any {
  const method = dunder(container, '__getitem__');
  if (method) return method(key);
  if (Array.isArray(container) || typeof container === 'string') {
    if (key instanceof Slice) {
      const items = key.range(container.length).map(i => container[i]);
      return typeof container === 'string' ? items.join('') : items;
    }
    if (Array.isArray(key) && Array.isArray(container) && hooks.asarray) return getitem(hooks.asarray(container), key);
    return container[sequenceIndex(container.length, key)];
  }
  if (container instanceof Map) {
    if (!container.has(key)) throw new Error(`KeyError: ${String(key)}`);
    return container instanceof PyDict ? container.lookup(key) : container.get(key);
  }
  if (isDict(container) && !Object.hasOwn(container, key)) throw new Error(`KeyError: ${String(key)}`);
  return container[key];
}

/** Python `container[key] = value`, with negative indices, slice assignment and `__setitem__`. */
export function setitem(container: any, key: any, value: any): void {
  const method = dunder(container, '__setitem__');
  if (method) {
    method(key, value);
  } else if (Array.isArray(container)) {
    if (key instanceof Slice) {
      const items = Array.from(value as Iterable<unknown>);
      if ((key.step ?? 1) === 1) {
        const [start, stop] = key.indices(container.length);
        container.splice(start, Math.max(0, stop - start), ...items);
      } else {
        const indices = key.range(container.length);
        if (indices.length !== items.length) throw new Error('ValueError: extended slice assignment size mismatch');
        indices.forEach((index, i) => (container[index] = items[i]));
      }
    } else if (Array.isArray(key) && hooks.asarray) {
      throw new TypeError('list indices must be integers or slices, not tuple');
    } else {
      container[sequenceIndex(container.length, key)] = value;
    }
  } else if (container instanceof Map) {
    container.set(key, value);
  } else {
    container[key] = value;
  }
}

/** Python `json.load(open(path))` and other reads of data files next to a module. */
export function readText(path: unknown): string {
  return new TextDecoder().decode(readResource(String(path)));
}

/** Identity of a key, as Python hashing sees it: tuples by value, entities by identity. */
function keyOf(key: unknown): unknown {
  if (Array.isArray(key)) return JSON.stringify(key.map(item => {
    const k = keyOf(item);
    return typeof k === 'object' && k !== null ? `@${(k as { id?(): number }).id?.() ?? ''}:${String((k as { filePointer?(): number }).filePointer?.() ?? '')}` : k;
  }));
  return key;
}

/**
 * Python `dict` (or `defaultdict`) with keys other than strings: tuples compare by value,
 * entities by identity, and numbers stay numbers.
 */
export class PyDict<K = any, V = any> extends Map<K, V> {
  private readonly keys_ = new Map<unknown, K>();

  constructor(entries?: Iterable<readonly [K, V]> | null, private readonly factory?: () => V) {
    super();
    for (const [key, value] of entries ?? []) this.set(key, value);
  }

  override get(key: K): V | undefined {
    const canonical = this.keys_.get(keyOf(key));
    if (canonical === undefined && this.factory) {
      const value = this.factory();
      this.set(key, value);
      return value;
    }
    return canonical === undefined ? undefined : super.get(canonical);
  }

  override set(key: K, value: V): this {
    const id = keyOf(key);
    const canonical = this.keys_.get(id) ?? key;
    this.keys_.set(id, canonical);
    return super.set(canonical, value);
  }

  override has(key: K): boolean {
    return this.keys_.has(keyOf(key));
  }

  override delete(key: K): boolean {
    const id = keyOf(key);
    const canonical = this.keys_.get(id);
    if (canonical === undefined) return false;
    this.keys_.delete(id);
    return super.delete(canonical);
  }

  /** Python `d.get(key, default)`, without creating defaultdict entries. */
  lookup(key: K, otherwise: V | null = null): V | null {
    const canonical = this.keys_.get(keyOf(key));
    return canonical === undefined ? otherwise : super.get(canonical)!;
  }

  override clear(): void {
    this.keys_.clear();
    super.clear();
  }

  setdefault(key: K, value: V): V {
    if (!this.has(key)) this.set(key, value);
    return this.lookup(key) as V;
  }

  pop(key: K, ...otherwise: [V?]): V {
    if (!this.has(key)) {
      if (otherwise.length) return otherwise[0] as V;
      throw new Error('KeyError');
    }
    const value = this.lookup(key) as V;
    this.delete(key);
    return value;
  }
}

/** Python `d.get(key, default)` on a Map or PyDict, without creating defaultdict entries. */
export function dictGet<K, V>(dict: Map<K, V>, key: K, otherwise: V | null = null): V | null {
  return dict instanceof PyDict ? dict.lookup(key, otherwise) : dict.has(key) ? dict.get(key)! : otherwise;
}

/** Python `d.setdefault(key, value)` on a Map or PyDict. */
export function dictSetdefault<K, V>(dict: Map<K, V>, key: K, value: V): V {
  if (!dict.has(key)) dict.set(key, value);
  return dictGet(dict, key) as V;
}

/** Python `d.pop(key[, default])` on a Map or PyDict. */
export function dictPop<K, V>(dict: Map<K, V>, key: K, ...otherwise: [V?]): V {
  if (!dict.has(key)) {
    if (otherwise.length) return otherwise[0] as V;
    throw new Error('KeyError');
  }
  const value = dictGet(dict, key) as V;
  dict.delete(key);
  return value;
}

/** Python `open(path)` for reading a data file next to a module; see `readResource` in ifcopenshell. */
export function open(path: unknown, mode = 'r'): { read(): string; close(): void } {
  if (!mode.startsWith('r')) throw new Error(`open(): only reading is supported, not mode ${mode}`);
  const text = readText(path);
  return { read: () => text, close: () => {} };
}
