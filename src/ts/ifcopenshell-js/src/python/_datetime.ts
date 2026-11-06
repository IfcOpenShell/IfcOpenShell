// This file was generated with the assistance of an AI coding tool.
// SPDX-License-Identifier: LGPL-3.0-or-later

// Python `datetime` for generated code: date, datetime, time, timedelta and fixed-offset
// timezones, with Python arithmetic (__add__, __sub__, ...), comparison and ISO formatting.
// Classes can be called without `new`, as in Python. Hand-written, unlike the
// transpiled util/ and api/ next to it.

import { NotImplemented as NOT_IMPLEMENTED } from './_py.js';

type Options = Record<string, unknown>;

/** Positional arguments and a trailing options object (Python keywords, snake_case or camelCase) by parameter name. */
export function bindArguments(names: string[], values: unknown[]): Record<string, any> {
  const last = values[values.length - 1];
  const options = last !== null && typeof last === 'object' && Object.getPrototypeOf(last) === Object.prototype
    ? (values.pop() as Options)
    : {};
  const result: Record<string, any> = {};
  names.forEach((name, i) => {
    const camel = name.replace(/_([a-z])/g, (_, c: string) => c.toUpperCase());
    result[name] = i < values.length ? values[i] : options[name] ?? options[camel];
  });
  return result;
}

/** A class that can also be called like a function, as Python classes are. */
export function pyclass<T extends abstract new (...args: any[]) => any>(cls: T): T & ((...args: ConstructorParameters<T>) => InstanceType<T>) {
  return new Proxy(cls, { apply: (target, _, args) => Reflect.construct(target, args) }) as any;
}

const pad = (value: number, width = 2) => String(Math.trunc(Math.abs(value))).padStart(width, '0');
const DAYS_IN_MONTH = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
const isLeap = (year: number) => year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
const daysInMonth = (year: number, month: number) => (month === 2 && isLeap(year) ? 29 : DAYS_IN_MONTH[month]!);
const daysBeforeYear = (year: number) => {
  const y = year - 1;
  return y * 365 + Math.floor(y / 4) - Math.floor(y / 100) + Math.floor(y / 400);
};
const daysBeforeMonth = (year: number, month: number) => {
  let days = 0;
  for (let m = 1; m < month; m++) days += daysInMonth(year, m);
  return days;
};
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const US_PER_DAY = 86_400_000_000;

function ordinalToDate(ordinal: number): [number, number, number] {
  // Python's _ord2ymd: 400, 100, 4 and 1 year cycles.
  let n = ordinal - 1;
  const n400 = Math.floor(n / 146097);
  n %= 146097;
  const n100 = Math.floor(n / 36524);
  n %= 36524;
  const n4 = Math.floor(n / 1461);
  n %= 1461;
  const n1 = Math.floor(n / 365);
  n %= 365;
  let year = n400 * 400 + n100 * 100 + n4 * 4 + n1 + 1;
  if (n1 === 4 || n100 === 4) return [year - 1, 12, 31];
  let month = 1;
  while (n >= daysInMonth(year, month)) n -= daysInMonth(year, month++);
  return [year, month, n + 1];
}

function checkDate(year: number, month: number, day: number): void {
  if (!Number.isInteger(year) || year < 1 || year > 9999) throw new Error(`ValueError: year ${year} is out of range`);
  if (!Number.isInteger(month) || month < 1 || month > 12) throw new Error('ValueError: month must be in 1..12');
  if (!Number.isInteger(day) || day < 1 || day > daysInMonth(year, month)) throw new Error('ValueError: day is out of range for month');
}

/** Python `datetime.timedelta`, normalised to days, seconds (0..86399) and microseconds (0..999999). */
class TimeDelta {
  readonly days: number;
  readonly seconds: number;
  readonly microseconds: number;

  constructor(...values: unknown[]) {
    const a = bindArguments(['days', 'seconds', 'microseconds', 'milliseconds', 'minutes', 'hours', 'weeks'], values);
    const total = Math.round(
      (((a.weeks ?? 0) * 7 + (a.days ?? 0)) * 86400 + (a.hours ?? 0) * 3600 + (a.minutes ?? 0) * 60 + (a.seconds ?? 0)) * 1e6
        + (a.milliseconds ?? 0) * 1000 + (a.microseconds ?? 0),
    );
    this.days = Math.floor(total / US_PER_DAY);
    const rest = total - this.days * US_PER_DAY;
    this.seconds = Math.floor(rest / 1e6);
    this.microseconds = rest - this.seconds * 1e6;
  }

  static fromMicroseconds(total: number): TimeDelta {
    return new TimeDelta(0, 0, total);
  }

  /** Total length in microseconds. */
  get total(): number {
    return this.days * US_PER_DAY + this.seconds * 1e6 + this.microseconds;
  }

  total_seconds(): number {
    return this.total / 1e6;
  }

  totalSeconds(): number {
    return this.total_seconds();
  }

  valueOf(): number {
    return this.total;
  }

  __bool__(): boolean {
    return this.total !== 0;
  }

  __eq__(other: unknown): boolean {
    return other instanceof TimeDelta && other.total === this.total;
  }

  __add__(other: unknown): unknown {
    if (other instanceof TimeDelta) return TimeDelta.fromMicroseconds(this.total + other.total);
    if (other instanceof PyDate) return other.__add__(this);
    return NOT_IMPLEMENTED;
  }

  __radd__(other: unknown): unknown {
    return this.__add__(other);
  }

  __sub__(other: unknown): unknown {
    return other instanceof TimeDelta ? TimeDelta.fromMicroseconds(this.total - other.total) : NOT_IMPLEMENTED;
  }

  __neg__(): TimeDelta {
    return TimeDelta.fromMicroseconds(-this.total);
  }

  __mul__(other: unknown): unknown {
    return typeof other === 'number' ? TimeDelta.fromMicroseconds(Math.round(this.total * other)) : NOT_IMPLEMENTED;
  }

  __rmul__(other: unknown): unknown {
    return this.__mul__(other);
  }

  __truediv__(other: unknown): unknown {
    if (other instanceof TimeDelta) return this.total / other.total;
    return typeof other === 'number' ? TimeDelta.fromMicroseconds(Math.round(this.total / other)) : NOT_IMPLEMENTED;
  }

  __floordiv__(other: unknown): unknown {
    if (other instanceof TimeDelta) return Math.floor(this.total / other.total);
    return typeof other === 'number' ? TimeDelta.fromMicroseconds(Math.floor(this.total / other)) : NOT_IMPLEMENTED;
  }

  __mod__(other: unknown): unknown {
    return other instanceof TimeDelta ? TimeDelta.fromMicroseconds(((this.total % other.total) + other.total) % other.total) : NOT_IMPLEMENTED;
  }

  /** Python `str(timedelta)`, such as `1 day, 2:03:04` or `0:00:00.500000`. */
  toString(): string {
    const hours = Math.floor(this.seconds / 3600);
    const minutes = Math.floor((this.seconds % 3600) / 60);
    let text = `${hours}:${pad(minutes)}:${pad(this.seconds % 60)}`;
    if (this.microseconds) text += `.${pad(this.microseconds, 6)}`;
    return this.days ? `${this.days} day${Math.abs(this.days) === 1 ? '' : 's'}, ${text}` : text;
  }

  static min = TimeDelta.fromMicroseconds(-999999999 * US_PER_DAY);
  static max = TimeDelta.fromMicroseconds(999999999 * US_PER_DAY + US_PER_DAY - 1);
  static resolution = TimeDelta.fromMicroseconds(1);
}

/** Python `datetime.timezone`: a fixed offset from UTC. */
class TimeZone {
  constructor(readonly offset: TimeDelta, readonly name: string | null = null) {}

  utcoffset(_value?: unknown): TimeDelta {
    return this.offset;
  }

  tzname(_value?: unknown): string {
    return this.name ?? (this.offset.total ? `UTC${formatOffset(this.offset, ':')}` : 'UTC');
  }

  __eq__(other: unknown): boolean {
    return other instanceof TimeZone && other.offset.total === this.offset.total;
  }

  static utc = new TimeZone(new TimeDelta(0));
}

function formatOffset(offset: TimeDelta, separator: string): string {
  const total = offset.total;
  const sign = total < 0 ? '-' : '+';
  const absolute = Math.abs(total);
  const hours = Math.floor(absolute / 3.6e9);
  const minutes = Math.floor((absolute % 3.6e9) / 6e7);
  const seconds = Math.floor((absolute % 6e7) / 1e6);
  const micro = absolute % 1e6;
  let text = `${sign}${pad(hours)}${separator}${pad(minutes)}`;
  if (seconds || micro) text += `${separator}${pad(seconds)}`;
  if (micro) text += `.${pad(micro, 6)}`;
  return text;
}

/** Python `strftime` directives for dates, datetimes and times. */
function strftime(format: string, value: { year?: number; month?: number; day?: number; hour?: number; minute?: number; second?: number; microsecond?: number; weekday?(): number; toordinal?(): number; tzinfo?: TimeZone | null }): string {
  const year = value.year ?? 1900;
  const month = value.month ?? 1;
  const day = value.day ?? 1;
  const hour = value.hour ?? 0;
  const weekday = value.weekday ? value.weekday() : 0;
  return format.replace(/%([a-zA-Z%])/g, (whole, code: string) => {
    switch (code) {
      case 'Y': return pad(year, 4);
      case 'y': return pad(year % 100);
      case 'm': return pad(month);
      case 'd': return pad(day);
      case 'H': return pad(hour);
      case 'I': return pad(hour % 12 || 12);
      case 'p': return hour < 12 ? 'AM' : 'PM';
      case 'M': return pad(value.minute ?? 0);
      case 'S': return pad(value.second ?? 0);
      case 'f': return pad(value.microsecond ?? 0, 6);
      case 'B': return MONTHS[month - 1]!;
      case 'b': return MONTHS[month - 1]!.slice(0, 3);
      case 'A': return WEEKDAYS[weekday]!;
      case 'a': return WEEKDAYS[weekday]!.slice(0, 3);
      case 'w': return String((weekday + 1) % 7);
      case 'j': return pad(daysBeforeMonth(year, month) + day, 3);
      case 'z': return value.tzinfo ? formatOffset(value.tzinfo.offset, '') : '';
      case 'Z': return value.tzinfo ? value.tzinfo.tzname() : '';
      case '%': return '%';
      default: return whole;
    }
  });
}

/** Python `datetime.date`. */
class PyDate {
  readonly year: number;
  readonly month: number;
  readonly day: number;

  constructor(...values: unknown[]) {
    const a = bindArguments(['year', 'month', 'day'], values);
    checkDate(a.year, a.month, a.day);
    this.year = a.year;
    this.month = a.month;
    this.day = a.day;
  }

  static today(): PyDate {
    const now = new Date();
    return new PyDate(now.getFullYear(), now.getMonth() + 1, now.getDate());
  }

  static fromordinal(ordinal: number): PyDate {
    return new PyDate(...ordinalToDate(ordinal));
  }

  static fromisoformat(text: string): PyDate {
    const match = /^(\d{4})-?(\d{2})-?(\d{2})$/.exec(String(text));
    if (!match) throw new Error(`ValueError: Invalid isoformat string: '${text}'`);
    return new PyDate(Number(match[1]), Number(match[2]), Number(match[3]));
  }

  static fromtimestamp(timestamp: number): PyDate {
    const value = new Date(timestamp * 1000);
    return new PyDate(value.getFullYear(), value.getMonth() + 1, value.getDate());
  }

  toordinal(): number {
    return daysBeforeYear(this.year) + daysBeforeMonth(this.year, this.month) + this.day;
  }

  /** Monday is 0. */
  weekday(): number {
    return (this.toordinal() + 6) % 7;
  }

  /** Monday is 1. */
  isoweekday(): number {
    return this.weekday() + 1;
  }

  isocalendar(): [number, number, number] {
    const ordinal = this.toordinal();
    const weekOneStart = (year: number) => {
      const first = daysBeforeYear(year) + 1;
      const weekday = (first + 6) % 7;
      return first - weekday + (weekday > 3 ? 7 : 0);
    };
    let year = this.year;
    if (ordinal < weekOneStart(year)) year--;
    else if (ordinal >= weekOneStart(year + 1)) year++;
    const offset = ordinal - weekOneStart(year);
    return [year, Math.floor(offset / 7) + 1, (offset % 7) + 1];
  }

  replace(...values: unknown[]): PyDate {
    const a = bindArguments(['year', 'month', 'day'], values);
    return new PyDate(a.year ?? this.year, a.month ?? this.month, a.day ?? this.day);
  }

  isoformat(): string {
    return `${pad(this.year, 4)}-${pad(this.month)}-${pad(this.day)}`;
  }

  strftime(format: string): string {
    return strftime(format, this);
  }

  toString(): string {
    return this.isoformat();
  }

  valueOf(): number {
    return this.toordinal() * 86400;
  }

  __eq__(other: unknown): boolean {
    return other instanceof PyDate && other.constructor === this.constructor && other.valueOf() === this.valueOf();
  }

  __add__(other: unknown): unknown {
    return other instanceof TimeDelta ? PyDate.fromordinal(this.toordinal() + other.days) : NOT_IMPLEMENTED;
  }

  __radd__(other: unknown): unknown {
    return this.__add__(other);
  }

  __sub__(other: unknown): unknown {
    if (other instanceof TimeDelta) return PyDate.fromordinal(this.toordinal() - other.days);
    if (other instanceof PyDate && !(other instanceof PyDateTime)) return new TimeDelta(this.toordinal() - other.toordinal());
    return NOT_IMPLEMENTED;
  }

  static min: PyDate;
  static max: PyDate;
  static resolution = new TimeDelta(1);
}

/** Python `datetime.time`. */
class PyTime {
  readonly hour: number;
  readonly minute: number;
  readonly second: number;
  readonly microsecond: number;
  readonly tzinfo: TimeZone | null;

  constructor(...values: unknown[]) {
    const a = bindArguments(['hour', 'minute', 'second', 'microsecond', 'tzinfo'], values);
    this.hour = a.hour ?? 0;
    this.minute = a.minute ?? 0;
    this.second = a.second ?? 0;
    this.microsecond = a.microsecond ?? 0;
    this.tzinfo = a.tzinfo ?? null;
    if (this.hour < 0 || this.hour > 23 || this.minute < 0 || this.minute > 59 || this.second < 0 || this.second > 59) {
      throw new Error('ValueError: time component out of range');
    }
  }

  static fromisoformat(text: string): PyTime {
    const parsed = parseTime(String(text));
    if (!parsed) throw new Error(`ValueError: Invalid isoformat string: '${text}'`);
    return new PyTime(...parsed);
  }

  replace(...values: unknown[]): PyTime {
    const a = bindArguments(['hour', 'minute', 'second', 'microsecond', 'tzinfo'], values);
    return new PyTime(a.hour ?? this.hour, a.minute ?? this.minute, a.second ?? this.second, a.microsecond ?? this.microsecond, a.tzinfo === undefined ? this.tzinfo : a.tzinfo);
  }

  utcoffset(): TimeDelta | null {
    return this.tzinfo?.offset ?? null;
  }

  isoformat(...values: unknown[]): string {
    const { timespec } = bindArguments(['timespec'], values);
    return formatTime(this, timespec) + (this.tzinfo ? formatOffset(this.tzinfo.offset, ':') : '');
  }

  strftime(format: string): string {
    return strftime(format, this);
  }

  toString(): string {
    return this.isoformat();
  }

  valueOf(): number {
    return this.hour * 3600 + this.minute * 60 + this.second + this.microsecond / 1e6;
  }

  __bool__(): boolean {
    return true;
  }

  __eq__(other: unknown): boolean {
    return other instanceof PyTime && other.valueOf() === this.valueOf();
  }

  static min: PyTime;
  static max: PyTime;
}

function formatTime(value: { hour: number; minute: number; second: number; microsecond: number }, timespec = 'auto'): string {
  const base = `${pad(value.hour)}:${pad(value.minute)}`;
  if (timespec === 'hours') return pad(value.hour);
  if (timespec === 'minutes') return base;
  const seconds = `${base}:${pad(value.second)}`;
  if (timespec === 'seconds' || (timespec === 'auto' && !value.microsecond)) return seconds;
  if (timespec === 'milliseconds') return `${seconds}.${pad(Math.floor(value.microsecond / 1000), 3)}`;
  return `${seconds}.${pad(value.microsecond, 6)}`;
}

/** [hour, minute, second, microsecond, tzinfo] of an ISO 8601 time, or null. */
function parseTime(text: string): [number, number, number, number, TimeZone | null] | null {
  const match = /^(\d{2})(?::?(\d{2})(?::?(\d{2})(?:[.,](\d+))?)?)?(Z|[+-]\d{2}(?::?\d{2}(?::?\d{2}(?:[.,]\d+)?)?)?)?$/.exec(text);
  if (!match) return null;
  const micro = match[4] ? Math.round(Number(`0.${match[4]}`) * 1e6) : 0;
  let zone: TimeZone | null = null;
  if (match[5]) {
    if (match[5] === 'Z') {
      zone = TimeZone.utc;
    } else {
      const sign = match[5][0] === '-' ? -1 : 1;
      const [hours, minutes = '0', seconds = '0'] = match[5].slice(1).match(/\d{2}(?:[.,]\d+)?/g)!;
      zone = new TimeZone(new TimeDelta(0, sign * (Number(hours) * 3600 + Number(minutes) * 60 + Number(seconds))));
    }
  }
  return [Number(match[1]), Number(match[2] ?? 0), Number(match[3] ?? 0), Math.min(micro, 999999), zone];
}

/** Python `datetime.datetime`; naive unless it has a fixed-offset tzinfo. */
class PyDateTime extends PyDate {
  static override min: PyDateTime;
  static override max: PyDateTime;
  readonly hour: number;
  readonly minute: number;
  readonly second: number;
  readonly microsecond: number;
  readonly tzinfo: TimeZone | null;

  constructor(...values: unknown[]) {
    const a = bindArguments(['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond', 'tzinfo'], values);
    super(a.year, a.month, a.day);
    const time = new PyTime(a.hour ?? 0, a.minute ?? 0, a.second ?? 0, a.microsecond ?? 0);
    this.hour = time.hour;
    this.minute = time.minute;
    this.second = time.second;
    this.microsecond = time.microsecond;
    this.tzinfo = a.tzinfo ?? null;
  }

  /** Microseconds since 0001-01-01 in local (naive) or wall-clock time. */
  private get wall(): number {
    return (this.toordinal() - 1) * US_PER_DAY + ((this.hour * 60 + this.minute) * 60 + this.second) * 1e6 + this.microsecond;
  }

  private static fromWall(wall: number, tzinfo: TimeZone | null): PyDateTime {
    const days = Math.floor(wall / US_PER_DAY);
    let rest = wall - days * US_PER_DAY;
    const [year, month, day] = ordinalToDate(days + 1);
    const hour = Math.floor(rest / 3.6e9);
    rest -= hour * 3.6e9;
    const minute = Math.floor(rest / 6e7);
    rest -= minute * 6e7;
    const second = Math.floor(rest / 1e6);
    return new PyDateTime(year, month, day, hour, minute, second, rest - second * 1e6, tzinfo);
  }

  static now(tz: TimeZone | null = null): PyDateTime {
    return PyDateTime.fromtimestamp(Date.now() / 1000, tz);
  }

  static today(): PyDateTime {
    return PyDateTime.now();
  }

  static fromtimestamp(timestamp: number, tz: TimeZone | null = null): PyDateTime {
    if (tz) return PyDateTime.fromWall(Math.round(timestamp * 1e6) + EPOCH + tz.offset.total, tz);
    const micro = Math.round(timestamp * 1e6);
    const value = new Date(Math.floor(micro / 1e6) * 1000);
    return new PyDateTime(
      value.getFullYear(), value.getMonth() + 1, value.getDate(), value.getHours(), value.getMinutes(), value.getSeconds(),
      micro - Math.floor(micro / 1e6) * 1e6,
    );
  }

  static utcfromtimestamp(timestamp: number): PyDateTime {
    return PyDateTime.fromWall(Math.round(timestamp * 1e6) + EPOCH, null);
  }

  static fromisoformat(text: string): PyDateTime {
    const value = String(text);
    const date = /^(\d{4})-?(\d{2})-?(\d{2})/.exec(value);
    if (!date) throw new Error(`ValueError: Invalid isoformat string: '${text}'`);
    const rest = value.slice(date[0].length);
    const time = rest ? parseTime(rest.slice(1)) : [0, 0, 0, 0, null];
    if (!time || (rest && !/^[T ]/i.test(rest))) throw new Error(`ValueError: Invalid isoformat string: '${text}'`);
    return new PyDateTime(Number(date[1]), Number(date[2]), Number(date[3]), ...time);
  }

  static combine(date: PyDate, time: PyTime, tzinfo?: TimeZone | null): PyDateTime {
    return new PyDateTime(date.year, date.month, date.day, time.hour, time.minute, time.second, time.microsecond, tzinfo === undefined ? time.tzinfo : tzinfo);
  }

  static strptime(text: string, format: string): PyDateTime {
    const fields: Record<string, number> = { Y: 1900, m: 1, d: 1, H: 0, M: 0, S: 0, f: 0, y: -1 };
    const order: string[] = [];
    const pattern = format.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/%([YmdHMSfy%])/g, (_, code: string) => {
      if (code === '%') return '%';
      order.push(code);
      return code === 'Y' ? '(\\d{4})' : code === 'f' ? '(\\d{1,6})' : '(\\d{1,2})';
    });
    const match = new RegExp(`^${pattern}$`).exec(String(text));
    if (!match) throw new Error(`ValueError: time data '${text}' does not match format '${format}'`);
    order.forEach((code, i) => (fields[code] = code === 'f' ? Number(match[i + 1]!.padEnd(6, '0')) : Number(match[i + 1])));
    const year = fields.y! >= 0 ? (fields.y! < 69 ? 2000 : 1900) + fields.y! : fields.Y!;
    return new PyDateTime(year, fields.m!, fields.d!, fields.H!, fields.M!, fields.S!, fields.f!);
  }

  date(): PyDate {
    return new PyDate(this.year, this.month, this.day);
  }

  time(): PyTime {
    return new PyTime(this.hour, this.minute, this.second, this.microsecond);
  }

  timetz(): PyTime {
    return new PyTime(this.hour, this.minute, this.second, this.microsecond, this.tzinfo);
  }

  utcoffset(): TimeDelta | null {
    return this.tzinfo?.offset ?? null;
  }

  override replace(...values: unknown[]): PyDateTime {
    const a = bindArguments(['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond', 'tzinfo'], values);
    return new PyDateTime(
      a.year ?? this.year, a.month ?? this.month, a.day ?? this.day, a.hour ?? this.hour, a.minute ?? this.minute,
      a.second ?? this.second, a.microsecond ?? this.microsecond, a.tzinfo === undefined ? this.tzinfo : a.tzinfo,
    );
  }

  astimezone(tz: TimeZone | null = null): PyDateTime {
    const target = tz ?? TimeZone.utc;
    return PyDateTime.fromWall(this.utc + target.offset.total, target);
  }

  /** POSIX timestamp; naive datetimes are local time, as in Python. */
  timestamp(): number {
    if (this.tzinfo) return (this.utc - EPOCH) / 1e6;
    const value = new Date(2000, this.month - 1, this.day, this.hour, this.minute, this.second);
    value.setFullYear(this.year);
    return value.getTime() / 1000 + this.microsecond / 1e6;
  }

  /** Microseconds since 0001-01-01 UTC (naive values are taken as UTC). */
  private get utc(): number {
    return this.wall - (this.tzinfo?.offset.total ?? 0);
  }

  override isoformat(...values: unknown[]): string {
    const { sep, timespec } = bindArguments(['sep', 'timespec'], values);
    return `${super.isoformat()}${sep ?? 'T'}${formatTime(this, timespec)}${this.tzinfo ? formatOffset(this.tzinfo.offset, ':') : ''}`;
  }

  override strftime(format: string): string {
    return strftime(format, this);
  }

  override toString(): string {
    return this.isoformat(' ');
  }

  override valueOf(): number {
    return this.utc / 1e6;
  }

  override __eq__(other: unknown): boolean {
    return other instanceof PyDateTime && other.utc === this.utc;
  }

  override __add__(other: unknown): unknown {
    return other instanceof TimeDelta ? PyDateTime.fromWall(this.wall + other.total, this.tzinfo) : NOT_IMPLEMENTED;
  }

  override __sub__(other: unknown): unknown {
    if (other instanceof TimeDelta) return PyDateTime.fromWall(this.wall - other.total, this.tzinfo);
    if (other instanceof PyDateTime) return TimeDelta.fromMicroseconds(this.utc - other.utc);
    return NOT_IMPLEMENTED;
  }
}

const EPOCH = 719162 * US_PER_DAY;
PyDate.min = new PyDate(1, 1, 1);
PyDate.max = new PyDate(9999, 12, 31);
PyTime.min = new PyTime(0, 0, 0, 0);
PyTime.max = new PyTime(23, 59, 59, 999999);
PyDateTime.min = new PyDateTime(1, 1, 1);
PyDateTime.max = new PyDateTime(9999, 12, 31, 23, 59, 59, 999999);

export const date = pyclass(PyDate);
export type date = PyDate;
export const datetime = pyclass(PyDateTime);
export type datetime = PyDateTime;
export const time = pyclass(PyTime);
export type time = PyTime;
export const timedelta = pyclass(TimeDelta);
export type timedelta = TimeDelta;
export const timezone = pyclass(TimeZone);
export type timezone = TimeZone;
