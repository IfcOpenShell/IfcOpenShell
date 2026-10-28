// This file was generated with the assistance of an AI coding tool.
// SPDX-License-Identifier: LGPL-3.0-or-later

// Python `itertools`, returning arrays as generated code does for generators.
// Hand-written; src/transpiler/generate.py copies it into src/.

export function chain<T>(...iterables: Iterable<T>[]): T[] {
  return iterables.flatMap(values => Array.from(values));
}

chain.fromIterable = <T>(iterables: Iterable<Iterable<T>>): T[] => Array.from(iterables).flatMap(values => Array.from(values));

export function product<T>(...iterables: Iterable<T>[]): T[][] {
  return iterables.reduce<T[][]>((result, values) => result.flatMap(prefix => Array.from(values, value => [...prefix, value])), [[]]);
}

export function pairwise<T>(values: Iterable<T>): [T, T][] {
  const items = Array.from(values);
  return items.slice(1).map((value, i) => [items[i]!, value]);
}

export function accumulate(values: Iterable<number>): number[] {
  let total = 0;
  return Array.from(values, value => (total += value));
}
