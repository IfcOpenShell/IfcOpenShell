// This file was generated with the assistance of an AI coding tool.
// SPDX-License-Identifier: LGPL-3.0-or-later

// Python `isodate` (0.7) for generated code: ISO 8601 durations.
// Hand-written, unlike the transpiled util/ and api/ next to it.

import { bindArguments, date as pydate, datetime as pydatetime, pyclass, timedelta } from './_datetime.js';
import { NotImplemented } from './_py.js';

export class ISO8601Error extends Error {}

const DAYS_IN_MONTH = (year: number, month: number) => new Date(Date.UTC(2000, month, 0)).getUTCDate() - (month === 2 && !(year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)) ? 1 : 0);

/** isodate.Duration: years and months, plus a timedelta for the rest. */
class IsoDuration {
  readonly years: number;
  readonly months: number;
  readonly tdelta: timedelta;

  constructor(...values: unknown[]) {
    const a = bindArguments(['days', 'seconds', 'microseconds', 'milliseconds', 'minutes', 'hours', 'weeks', 'months', 'years'], values);
    this.years = a.years ?? 0;
    this.months = a.months ?? 0;
    this.tdelta = timedelta(a.days ?? 0, a.seconds ?? 0, a.microseconds ?? 0, a.milliseconds ?? 0, a.minutes ?? 0, a.hours ?? 0, a.weeks ?? 0);
  }

  private static of(years: number, months: number, tdelta: timedelta): IsoDuration {
    const duration = new IsoDuration({ years, months });
    (duration as { tdelta: timedelta }).tdelta = tdelta;
    return duration;
  }

  get days(): number {
    return this.tdelta.days;
  }

  get seconds(): number {
    return this.tdelta.seconds;
  }

  get microseconds(): number {
    return this.tdelta.microseconds;
  }

  totimedelta(...values: unknown[]): timedelta {
    const { start, end } = bindArguments(['start', 'end'], values);
    if (start != null) return (this.__add__(start) as any).__sub__(start);
    return (end as any).__sub__(this.__rsub__(end));
  }

  __neg__(): IsoDuration {
    return IsoDuration.of(-this.years, -this.months, this.tdelta.__neg__());
  }

  __add__(other: unknown): unknown {
    if (other instanceof IsoDuration) return IsoDuration.of(this.years + other.years, this.months + other.months, this.tdelta.__add__(other.tdelta) as timedelta);
    if (other instanceof timedelta) return IsoDuration.of(this.years, this.months, this.tdelta.__add__(other) as timedelta);
    if (other instanceof pydate) return shift(other, this.years, this.months).__add__(this.tdelta);
    return NotImplemented;
  }

  __radd__(other: unknown): unknown {
    return this.__add__(other);
  }

  __sub__(other: unknown): unknown {
    if (other instanceof IsoDuration) return IsoDuration.of(this.years - other.years, this.months - other.months, this.tdelta.__sub__(other.tdelta) as timedelta);
    if (other instanceof timedelta) return IsoDuration.of(this.years, this.months, this.tdelta.__sub__(other) as timedelta);
    return NotImplemented;
  }

  __rsub__(other: unknown): unknown {
    if (other instanceof pydate) return shift(other, -this.years, -this.months).__sub__(this.tdelta);
    if (other instanceof timedelta) return IsoDuration.of(-this.years, -this.months, other.__sub__(this.tdelta) as timedelta);
    return NotImplemented;
  }

  __mul__(other: unknown): unknown {
    return typeof other === 'number' ? IsoDuration.of(this.years * other, this.months * other, this.tdelta.__mul__(other) as timedelta) : NotImplemented;
  }

  __rmul__(other: unknown): unknown {
    return this.__mul__(other);
  }

  __eq__(other: unknown): boolean {
    if (other instanceof IsoDuration) return this.years * 12 + this.months === other.years * 12 + other.months && this.tdelta.__eq__(other.tdelta);
    if (other instanceof timedelta) return !this.years && !this.months && this.tdelta.__eq__(other);
    return false;
  }

  __bool__(): boolean {
    return Boolean(this.years || this.months || this.tdelta.total);
  }

  toString(): string {
    const parts: string[] = [];
    if (this.years) parts.push(`${this.years} years`);
    if (this.months) parts.push(`${this.months} month${this.months === 1 ? '' : 's'}`);
    parts.push(String(this.tdelta));
    return parts.join(', ');
  }
}

/** A date moved by whole years and months, with the day clamped to the month's length, as isodate does. */
function shift(value: pydate, years: number, months: number): any {
  if (!Number.isInteger(years) || !Number.isInteger(months)) throw new Error('ValueError: fractional years or months not supported for date calculations');
  const total = value.month - 1 + months;
  const year = value.year + years + Math.floor(total / 12);
  const month = ((total % 12) + 12) % 12 + 1;
  return value.replace({ year, month, day: Math.min(value.day, DAYS_IN_MONTH(year, month)) });
}

export const Duration = pyclass(IsoDuration);
export type Duration = IsoDuration;

const PERIOD = /^([+-])?P(?!\b)(?:(\d+(?:[,.]\d+)?)Y)?(?:(\d+(?:[,.]\d+)?)M)?(?:(\d+(?:[,.]\d+)?)W)?(?:(\d+(?:[,.]\d+)?)D)?(?:T(?:(\d+(?:[,.]\d+)?)H)?(?:(\d+(?:[,.]\d+)?)M)?(?:(\d+(?:[,.]\d+)?)S)?)?$/;

/** isodate.parse_duration: a timedelta, or a Duration when there are years or months. */
export function parseDuration(text: string, ...values: unknown[]): timedelta | IsoDuration {
  const { as_timedelta_if_possible: asTimedelta = true } = bindArguments(['as_timedelta_if_possible'], values);
  if (typeof text !== 'string') throw new TypeError(`Expecting a string ${String(text)}`);
  const match = PERIOD.exec(text);
  if (!match) {
    if (text.startsWith('P')) {
      // Alternative format, PYYYY-MM-DDThh:mm:ss.
      const parts = /^P(\d{4})-?(\d{2})-?(\d{2})T(\d{2}):?(\d{2}):?(\d{2})(?:[.,](\d+))?$/.exec(text);
      if (parts) {
        const [years, months, days, hours, minutes, seconds] = parts.slice(1, 7).map(Number) as number[];
        const microseconds = parts[7] ? Math.round(Number(`0.${parts[7]}`) * 1e6) : 0;
        return asTimedelta && !years && !months
          ? timedelta({ days, seconds, microseconds, minutes, hours })
          : Duration({ days, seconds, microseconds, minutes, hours, months, years });
      }
    }
    throw new ISO8601Error(`Unable to parse duration string '${text}'`);
  }
  const [years, months, weeks, days, hours, minutes, seconds] = match.slice(2).map(v => Number((v ?? '0').replace(',', '.')));
  const negative = match[1] === '-';
  if (asTimedelta && !years && !months) {
    const result = timedelta({ days, hours, minutes, seconds, weeks });
    return negative ? (result.__neg__()) : result;
  }
  const result = Duration({ years, months, days, hours, minutes, seconds, weeks });
  return negative ? result.__neg__() : result;
}

/** isodate.duration_isoformat with the default format, P%P. */
export function durationIsoformat(duration: timedelta | IsoDuration, format = 'P%P'): string {
  const negative = duration instanceof IsoDuration
    ? duration.years < 0 || duration.months < 0 || duration.tdelta.total < 0
    : duration.total < 0;
  return (negative ? '-' : '') + strftimeDuration(duration, format);
}

function strftimeDuration(duration: timedelta | IsoDuration, format: string): string {
  return format.replace(/%P|%p|%%/g, code => {
    if (code === '%%') return '%';
    if (code === '%p') return `${Math.abs(Math.floor(duration.days / 7))}W`;
    const result: string[] = [];
    if (duration instanceof IsoDuration) {
      if (duration.years) result.push(`${Math.abs(duration.years)}Y`);
      if (duration.months) result.push(`${Math.abs(duration.months)}M`);
    }
    let usecs = Math.abs((duration.days * 86400 + duration.seconds) * 1e6 + duration.microseconds);
    let seconds = Math.floor(usecs / 1e6);
    usecs -= seconds * 1e6;
    let minutes = Math.floor(seconds / 60);
    seconds %= 60;
    let hours = Math.floor(minutes / 60);
    minutes %= 60;
    const days = Math.floor(hours / 24);
    hours %= 24;
    if (days) result.push(`${days}D`);
    if (hours || minutes || seconds || usecs) {
      result.push('T');
      if (hours) result.push(`${hours}H`);
      if (minutes) result.push(`${minutes}M`);
      if (seconds || usecs) {
        result.push(usecs ? `${seconds}.${String(usecs).padStart(6, '0')}`.replace(/0+$/, '') : String(seconds));
        result.push('S');
      }
    }
    return result.length ? result.join('') : '0D';
  });
}
