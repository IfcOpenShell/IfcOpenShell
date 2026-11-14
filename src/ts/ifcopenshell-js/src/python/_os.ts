// This file was generated with the assistance of an AI coding tool.
// SPDX-License-Identifier: LGPL-3.0-or-later

// Python `os.path` for locating data files next to a module. Paths are plain paths or file URLs.
// Hand-written, unlike the transpiled util/ and api/ next to it.

function strip(value: string): string {
  return value.startsWith('file:') ? decodeURIComponent(new URL(value).pathname) : value;
}

const lastSeparator = (text: string) => Math.max(text.lastIndexOf('/'), text.lastIndexOf('\\'));

export const path = {
  sep: '/',
  join(first: string, ...parts: string[]): string {
    return parts.reduce((joined, part) => (/^([\\/]|[A-Za-z]:)/.test(part) ? part : `${joined.replace(/[\\/]+$/, '')}/${part}`), String(first));
  },
  dirname(value: string): string {
    const text = strip(String(value));
    const index = lastSeparator(text);
    return index < 0 ? '' : index === 0 ? text.slice(0, 1) : text.slice(0, index);
  },
  basename(value: string): string {
    const text = String(value);
    return text.slice(lastSeparator(text) + 1);
  },
  splitext(value: string): [string, string] {
    const text = String(value);
    const base = path.basename(text);
    const dot = base.lastIndexOf('.');
    return dot <= 0 ? [text, ''] : [text.slice(0, text.length - base.length + dot), base.slice(dot)];
  },
  realpath(value: string): string {
    return strip(String(value));
  },
  abspath(value: string): string {
    return strip(String(value));
  },
};
