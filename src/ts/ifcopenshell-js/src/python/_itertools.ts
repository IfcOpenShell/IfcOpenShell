// This file was generated with the assistance of an AI coding tool.
// SPDX-License-Identifier: LGPL-3.0-or-later

// Python `itertools`, returning arrays as generated code does for generators.
// Hand-written, unlike the transpiled util/ and api/ next to it.

export function chain<T>(...iterables: Iterable<T>[]): T[] {
  return iterables.flatMap(values => Array.from(values));
}
