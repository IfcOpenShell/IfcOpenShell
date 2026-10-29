// This file was generated with the assistance of an AI coding tool.

// The hand-written runtime of ifcopenshell/util and ifcopenshell/api (numpy, datetime, isodate, dateutil, str.format)
// against values computed with Python 3.13, numpy 2.3, isodate 0.7 and dateutil 2.9.

import { describe, expect, it } from 'vitest';
import * as py from '../../dist/python/_py.js';
import * as np from '../../dist/python/_numpy.js';
import * as datetime from '../../dist/python/_datetime.js';
import * as isodate from '../../dist/python/_isodate.js';
import { parser } from '../../dist/python/_dateutil.js';

const close = (actual: unknown, expected: unknown) => {
  const flat = (v: unknown): number[] => (Array.isArray(v) ? v.flatMap(flat) : [Number(v)]);
  const a = flat(actual);
  const b = flat(expected);
  expect(a.length).toBe(b.length);
  a.forEach((x, i) => expect(x).toBeCloseTo(b[i]!, 9));
};

describe('datetime', () => {
  it('formats timedeltas as Python str()', () => {
    expect([
      String(datetime.timedelta({ seconds: 3725 })),
      String(datetime.timedelta({ days: 1, hours: 2 })),
      String(datetime.timedelta({ days: -1, seconds: 5 })),
      String(datetime.timedelta({ milliseconds: 500 })),
    ]).toEqual(['1:02:05', '1 day, 2:00:00', '-1 day, 0:00:05', '0:00:00.500000']);
  });

  it('does date arithmetic and formatting', () => {
    const d = datetime.datetime(2024, 2, 28, 22, 30);
    expect(py.add(d, datetime.timedelta({ hours: 3 })).isoformat()).toBe('2024-02-29T01:30:00');
    expect(py.sub(datetime.date(2024, 3, 1), datetime.date(2023, 3, 1)).days).toBe(366);
    expect(datetime.date(2024, 1, 1).weekday()).toBe(0);
    expect(datetime.date(2021, 1, 3).isocalendar()).toEqual([2020, 53, 7]);
    expect(d.strftime('%d/%m/%y %H:%M %a %b %j')).toBe('28/02/24 22:30 Wed Feb 059');
    expect(datetime.datetime.fromisoformat('2020-05-06T07:08:09.5+02:00').isoformat()).toBe('2020-05-06T07:08:09.500000+02:00');
    expect(datetime.date(2024, 1, 31).toordinal()).toBe(738916);
    expect(datetime.date(2024, 1, 31) instanceof datetime.date).toBe(true);
    expect(d instanceof datetime.date).toBe(true);
    expect(d < datetime.datetime(2024, 3, 1)).toBe(true);
    expect(py.eq(datetime.date(2024, 1, 1), datetime.date(2024, 1, 1))).toBe(true);
  });
});

describe('isodate and dateutil', () => {
  it('formats durations as isodate.duration_isoformat', () => {
    expect([
      isodate.durationIsoformat(datetime.timedelta({ days: 3, hours: 4, minutes: 5, seconds: 6.5 })),
      isodate.durationIsoformat(datetime.timedelta(0)),
      isodate.durationIsoformat(isodate.parseDuration('P1Y2M3DT4H')),
      isodate.durationIsoformat(py.neg(datetime.timedelta({ hours: 5 }))),
      isodate.durationIsoformat(datetime.timedelta({ weeks: 2 })),
    ]).toEqual(['P3DT4H5M6.5S', 'P0D', 'P1Y2M3DT4H', '-PT5H', 'P14D']);
  });

  it('parses durations', () => {
    expect(String(isodate.parseDuration('PT36H'))).toBe('1 day, 12:00:00');
    expect(isodate.parseDuration('P1M')).toBeInstanceOf(isodate.Duration);
    expect(py.add(datetime.date(2024, 1, 31), isodate.parseDuration('P1M')).isoformat()).toBe('2024-02-29');
  });

  it('parses dates as dateutil', () => {
    expect([
      parser.isoparse('2021-03-04').isoformat(),
      parser.parse('04/03/2021', { dayfirst: true }).isoformat(),
      parser.parse('March 4 2021 10:30').isoformat(),
    ]).toEqual(['2021-03-04T00:00:00', '2021-03-04T00:00:00', '2021-03-04T10:30:00']);
  });
});

describe('str.format', () => {
  it('follows the format specification mini-language', () => {
    expect([
      py.format('{:d}+{:0{}.{}f}', 12, 3.14159, 7, 3),
      py.format('{0:.2f}', 2.005),
      py.format('{:>8}|{:<5}|{:^7}', 'a', 'b', 'c'),
      py.format('{:,}', 1234567),
      py.format('{:+.1e}', 12345.678),
      py.format('{:g}', 0.0001234),
      py.format('{name}!', { name: 'x' }),
    ]).toEqual(['12+003.142', '2.00', '       a|b    |   c   ', '1,234,567', '+1.2e+04', '0.0001234', 'x!']);
  });
});

describe('numpy', () => {
  const m = () => np.array([[1, 2], [3, 4]], { dtype: np.float64 });

  it('indexes with views, slices, masks and lists', () => {
    const a = np.eye(4);
    py.setitem(a, [py.slice(null, 3), 3], [1, 2, 3]);
    expect(py.getitem(a, [py.slice(null, 3), 3]).tolist()).toEqual([1, 2, 3]);
    expect(a.T.tolist()).toEqual([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [1, 2, 3, 1]]);
    expect(py.getitem(m(), [py.slice(null, null), 1]).tolist()).toEqual([2, 4]);
    const v = np.array([5, 6, 7]);
    expect(py.getitem(v, new py.IndexList([0, 2])).tolist()).toEqual([5, 7]);
    expect(py.getitem(v, py.sub(v, 5).__gt__(0)).tolist()).toEqual([6, 7]);
    expect(py.getitem(np.array([1, 2, 3]), py.slice(null, null, -1)).tolist()).toEqual([3, 2, 1]);
    expect(py.getitem(np.array([1, 2]), [py.slice(null, null), np.newaxis]).tolist()).toEqual([[1], [2]]);
    // Rows iterated from an array are views: writing to them changes the array.
    const axes = np.eye(3);
    for (const axis of axes) py.setitem(axis, py.slice(null, 1), [9]);
    expect(axes.tolist()).toEqual([[9, 0, 0], [9, 1, 0], [9, 0, 1]]);
  });

  it('does broadcasting arithmetic through Python operators', () => {
    expect(py.add(m(), np.array([10, 20])).tolist()).toEqual([[11, 22], [13, 24]]);
    expect(py.neg(m()).tolist()).toEqual([[-1, -2], [-3, -4]]);
    expect(py.sub(1, m()).tolist()).toEqual([[0, -1], [-2, -3]]);
    expect(py.matmul(m(), m()).tolist()).toEqual([[7, 10], [15, 22]]);
    expect(py.matmul(m(), np.array([1, 1])).tolist()).toEqual([3, 7]);
    const x = np.zeros(3);
    const alias = x;
    py.imul(py.iadd(x, 2), 3);
    expect(alias.tolist()).toEqual([6, 6, 6]);
  });

  it('implements linear algebra and array functions', () => {
    close(np.linalg.inv(m()).tolist(), [[-2, 1], [1.5, -0.5]]);
    expect(np.linalg.norm([3, 4])).toBe(5);
    close(np.linalg.norm(m()), 5.477225575051661);
    close(np.linalg.norm(m(), { axis: 1 }).tolist(), [2.23606797749979, 5]);
    expect(np.cross([1, 0, 0], [0, 1, 0]).tolist()).toEqual([0, 0, 1]);
    expect(np.array([0, 1, 2, 3, 4, 5]).reshape([2, 3], { order: 'F' }).tolist()).toEqual([[0, 2, 4], [1, 3, 5]]);
    expect(np.concatenate([m(), m()], { axis: 1 }).tolist()).toEqual([[1, 2, 1, 2], [3, 4, 3, 4]]);
    expect(np.vstack([[1, 2], [3, 4]]).tolist()).toEqual([[1, 2], [3, 4]]);
    expect(np.where(np.array([1, -1, 2]).__gt__(0), 1, 0).tolist()).toEqual([1, 0, 1]);
    expect(np.sum(m(), { axis: 0 }).tolist()).toEqual([4, 6]);
    expect(np.allclose([1, 2], [1, 2 + 1e-9])).toBe(true);
    expect(np.delete(np.array([1, 2, 3, 4]), [1, 2]).tolist()).toEqual([1, 4]);
    expect(np.append([1, 2], [[3, 4]]).tolist()).toEqual([1, 2, 3, 4]);
    expect(np.round(np.array([0.5, 1.5, 2.25]), 1).tolist()).toEqual([0.5, 1.5, 2.2]);
  });
});
