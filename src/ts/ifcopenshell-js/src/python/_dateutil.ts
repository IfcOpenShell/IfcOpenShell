// This file was generated with the assistance of an AI coding tool.
// SPDX-License-Identifier: LGPL-3.0-or-later

// Python `dateutil.parser` for generated code: ISO 8601 parsing and a lenient parser for common
// day/month/year formats. Hand-written, unlike the transpiled util/ and api/ next to it.

import { bindArguments, datetime } from './_datetime.js';

const MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];

class ParserError extends Error {}

/** dateutil.parser.isoparse: dates (as midnight), and dates with times and offsets. */
function isoparse(text: string): datetime {
  const value = String(text).trim();
  const month = /^(\d{4})-(\d{2})$/.exec(value);
  if (month) return datetime(Number(month[1]), Number(month[2]), 1);
  if (/^\d{4}$/.test(value)) return datetime(Number(value), 1, 1);
  try {
    return datetime.fromisoformat(value.replace(/^(\d{4}-?\d{2}-?\d{2})t/, '$1T'));
  } catch {
    throw new Error(`ValueError: Invalid isoformat string: '${text}'`);
  }
}

/**
 * dateutil.parser.parse for the formats people type: ISO dates, `d/m/y` or `m/d/y` (see
 * `dayfirst`), month names, and an optional `H:M[:S]` time. `fuzzy` ignores other words.
 */
function parse(text: string, ...values: unknown[]): datetime {
  const { dayfirst = false, yearfirst = false, fuzzy = false } = bindArguments(['parserinfo', 'dayfirst', 'yearfirst', 'fuzzy'], values.length === 1 ? values : [null, ...values]);
  const value = String(text).trim();
  try {
    return isoparse(value);
  } catch {
    // Not ISO 8601.
  }
  const now = datetime.now();
  let hour = 0;
  let minute = 0;
  let second = 0;
  let rest = value.replace(/(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([ap]\.?m\.?)?/i, (_, h: string, m: string, s?: string, meridiem?: string) => {
    hour = Number(h) % (meridiem ? 12 : 24) + (meridiem && /^p/i.test(meridiem) ? 12 : 0);
    minute = Number(m);
    second = Number(s ?? 0);
    return ' ';
  });
  let monthName: number | null = null;
  rest = rest.replace(/[a-z]+/gi, word => {
    const index = MONTHS.indexOf(word.slice(0, 3).toLowerCase());
    if (index >= 0 && monthName === null) {
      monthName = index + 1;
      return ' ';
    }
    if (!fuzzy && !/^(t|at|on|of|the|st|nd|rd|th)$/i.test(word)) throw new ParserError(`Unknown string format: ${text}`);
    return ' ';
  });
  const numbers = rest.match(/\d+/g)?.map(Number) ?? [];
  let year = now.year;
  let month = now.month;
  let day = now.day;
  if (monthName !== null) {
    month = monthName;
    const yearIndex = numbers.findIndex(n => n > 31);
    if (yearIndex >= 0) year = numbers.splice(yearIndex, 1)[0]!;
    if (numbers.length) day = numbers.shift()!;
    if (numbers.length) year = numbers.shift()!;
  } else if (numbers.length >= 3) {
    let [a, b, c] = numbers as [number, number, number];
    if (a > 31 || yearfirst) [year, month, day] = [a, b, c];
    else if (dayfirst || a > 12) [day, month, year] = [a, b, c];
    else [month, day, year] = [a, b, c];
  } else if (numbers.length === 2) {
    [day, month] = dayfirst || numbers[0]! > 12 ? numbers as [number, number] : [numbers[1]!, numbers[0]!];
  } else if (numbers.length === 1 && hour === 0 && minute === 0) {
    day = numbers[0]!;
  } else if (!numbers.length && monthName === null && !/\d/.test(value)) {
    throw new ParserError(`String does not contain a date: ${text}`);
  }
  if (year < 100) year += year < 69 ? 2000 : 1900;
  try {
    return datetime(year, month, day, hour, minute, second);
  } catch (error) {
    throw new ParserError(`${(error as Error).message}: ${text}`);
  }
}

export const parser = { isoparse, parse, ParserError };
