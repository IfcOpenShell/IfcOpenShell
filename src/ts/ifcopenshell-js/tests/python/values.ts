// This file was generated with the assistance of an AI coding tool.

// Encoding shared with src/transpiler/parity/record.py: entities are {"#": id, "type": ...},
// inline typed values {"$type": ..., "value": ...}, dicts {"$dict": [[k, v], ...]},
// sets {"$set": [...]}, files {"$file": index}, non-finite floats {"$float": "inf"}, numpy arrays
// {"$ndarray": [...]}, and datetime values {"$datetime"|"$date"|"$time": iso, "$timedelta": [d, s, us],
// "$duration": [years, months, d, s, us]} (isodate.Duration).

import * as ifcopenshell from 'ifcopenshell';
import { PyDict } from '../../dist/python/_py.js';
import { NDArray, array } from '../../dist/python/_numpy.js';
import * as datetime from '../../dist/python/_datetime.js';
import * as isodate from '../../dist/python/_isodate.js';

export type Encoded = null | boolean | number | string | Encoded[] | { [key: string]: Encoded };

/** Masked like record.py so generated GlobalIds and timestamps compare equal. */
const MASKED: Record<string, string> = {
  GlobalId: '$guid', CreationDate: '$time', LastModifiedDate: '$time', Version: '$version',
  UpdateDate: '$time', StartTime: '$time', HourComponent: '$time', MinuteComponent: '$time', SecondComponent: '$time',
};

export class Unreplayable extends Error {}

function isEntity(value: unknown): value is ifcopenshell.EntityInstance {
  return value instanceof ifcopenshell.EntityInstance;
}

export function encode(value: unknown, files: ifcopenshell.File[]): Encoded {
  if (value === null || value === undefined) return null;
  if (typeof value === 'boolean' || typeof value === 'string') return value;
  if (typeof value === 'bigint') return Number(value);
  if (typeof value === 'number') {
    if (Number.isFinite(value)) return value;
    return { $float: Number.isNaN(value) ? 'nan' : value > 0 ? 'inf' : '-inf' };
  }
  if (isEntity(value)) {
    return value.id() === 0
      ? { $type: value.isA(), value: encode(value.wrappedValue, files) }
      : { '#': value.id(), type: value.isA() };
  }
  if (value instanceof ifcopenshell.File) {
    // A file the call created is numbered after the input files, as record.py does.
    if (!files.includes(value)) files.push(value);
    return { $file: files.indexOf(value) };
  }
  if (value instanceof NDArray) return { $ndarray: encode(value.tolist(), files) };
  if (value instanceof datetime.datetime) return { $datetime: value.isoformat() };
  if (value instanceof datetime.date) return { $date: value.isoformat() };
  if (value instanceof datetime.time) return { $time: value.isoformat() };
  if (value instanceof datetime.timedelta) return { $timedelta: [value.days, value.seconds, value.microseconds] };
  if (value instanceof isodate.Duration) {
    return { $duration: [value.years, value.months, value.tdelta.days, value.tdelta.seconds, value.tdelta.microseconds] };
  }
  if (Array.isArray(value)) {
    // Generated NamedTuples are arrays with named fields.
    const fields = Object.keys(value).filter(key => !/^\d+$/.test(key));
    const items = value.map(v => encode(v, files));
    return fields.length ? { $fields: fields, $tuple: items } : items;
  }
  if (value instanceof Set) return { $set: [...value].map(v => encode(v, files)) };
  if (value instanceof Map) return { $dict: [...value].map(([k, v]) => [encode(k, files), encode(v, files)]) };
  if (typeof value === 'object') {
    return { $dict: Object.entries(value).map(([k, v]) => [k, encode(v, files)]) };
  }
  throw new Unreplayable(`cannot encode ${typeof value}`);
}

export function decode(value: Encoded, files: ifcopenshell.File[]): unknown {
  if (value === null || typeof value !== 'object') return value;
  if (Array.isArray(value)) return value.map(v => decode(v, files));
  if ('$file' in value) return files[value.$file as number];
  if ('#' in value) {
    const file = files[value.$f as number];
    if (!file) throw new Unreplayable('entity argument from an unrecorded file');
    return file.byId(value['#'] as number);
  }
  if ('$type' in value) {
    // An inline typed value such as IfcLengthMeasure(5), which IFC files do not store as entities.
    if (!files[0]) throw new Unreplayable('typed value without a file');
    return files[0].create(value.$type as string, [decode(value.value as Encoded, files) as never]);
  }
  if ('$tuple' in value) {
    // A NamedTuple: an array with named fields, as generated code builds them.
    const items = (value.$tuple as Encoded[]).map(v => decode(v, files));
    return Object.assign(items, Object.fromEntries((value.$fields as string[]).map((f, i) => [f, items[i]])));
  }
  if ('$ndarray' in value) return array(decode(value.$ndarray as Encoded, files) as never);
  if ('$datetime' in value) return datetime.datetime.fromisoformat(value.$datetime as string);
  if ('$date' in value) return datetime.date.fromisoformat(value.$date as string);
  if ('$time' in value) return datetime.time.fromisoformat(value.$time as string);
  if ('$timedelta' in value) {
    const [days, seconds, microseconds] = value.$timedelta as number[];
    return datetime.timedelta(days, seconds, microseconds);
  }
  if ('$duration' in value) {
    const [years, months, days, seconds, microseconds] = value.$duration as number[];
    return isodate.Duration({ years, months, days, seconds, microseconds });
  }
  if ('$float' in value) return { inf: Infinity, '-inf': -Infinity, nan: NaN }[value.$float as string];
  if ('$set' in value) return new Set((value.$set as Encoded[]).map(v => decode(v, files)));
  if ('$dict' in value) {
    const entries = (value.$dict as [Encoded, Encoded][]).map(([k, v]) => [decode(k, files), decode(v, files)] as const);
    // String-keyed dicts are plain objects in generated code; anything else is a Map.
    return entries.every(([k]) => typeof k === 'string') ? Object.fromEntries(entries) : new PyDict(entries);
  }
  throw new Unreplayable(`cannot decode argument ${JSON.stringify(value).slice(0, 80)}`);
}

const setAttributeCache = new Map<string, Set<string>>();

/** Names of the attributes declared as SET aggregates, which IFC leaves unordered. */
function setAttributes(entity: ifcopenshell.EntityInstance): Set<string> {
  const key = entity.isA(true);
  let names = setAttributeCache.get(key);
  if (!names) {
    const attributes = entity.declaration().asEntity()?.allAttributes() ?? [];
    names = new Set(attributes
      .filter(a => a.typeOfAttribute()?.asAggregationType()?.typeOfAggregationString() === 'set')
      .map(a => a.name()));
    setAttributeCache.set(key, names);
  }
  return names;
}

/** Flat attributes of every entity, as record.py's Call.graph. */
export function graph(file: ifcopenshell.File, files: ifcopenshell.File[]): Encoded {
  return file.ids.map((id) => {
    const entity = file.byId(id);
    const sets = setAttributes(entity);
    return Object.fromEntries(Object.entries(entity.getInfo()).map(([k, v]) => [
      k,
      k in MASKED && v !== null && v !== undefined
        ? MASKED[k]!
        : sets.has(k) && Array.isArray(v) ? { $set: encode(v, files) } : encode(v, files),
    ])) as Encoded;
  });
}

export interface Changes {
  changed: Encoded[];
  removed: number[];
}

/** Entities added or modified between two graphs, and ids removed, as record.py's Call.changes. */
export function changes(before: Encoded, after: Encoded): Changes {
  const byId = (graph: Encoded) => new Map((graph as Record<string, Encoded>[]).map(e => [e.id as number, e as Encoded]));
  const previous = byId(before);
  const current = byId(after);
  return {
    changed: [...current].filter(([id, e]) => !previous.has(id) || difference(e, previous.get(id)!) !== null).map(([, e]) => e),
    removed: [...previous.keys()].filter(id => !current.has(id)).sort((a, b) => a - b),
  };
}

function canonical(value: Encoded): Encoded {
  if (value === null || typeof value !== 'object') return value;
  if (Array.isArray(value)) return value.map(canonical);
  const sorted = (items: Encoded[]) => items.sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)));
  if ('$dict' in value) {
    // Python int keys become strings as JS object keys.
    return { $dict: sorted((value.$dict as [Encoded, Encoded][]).map(([k, v]) => [typeof k === 'number' ? String(k) : canonical(k), canonical(v)])) };
  }
  if ('$set' in value) return { $set: sorted((value.$set as Encoded[]).map(canonical)) };
  return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, canonical(v)]));
}

/** First difference between two encoded values, or null; floats use a relative tolerance. */
export function difference(actual: Encoded, expected: Encoded, tolerance = 1e-9): string | null {
  const walk = (a: Encoded, e: Encoded, path: string): string | null => {
    if (typeof a === 'number' && typeof e === 'number') {
      return a === e || Math.abs(a - e) <= tolerance * Math.max(Math.abs(a), Math.abs(e)) + 1e-12
        ? null
        : `${path}: ${a} != ${e}`;
    }
    if (a === null || e === null || typeof a !== 'object' || typeof e !== 'object') {
      return a === e ? null : `${path}: ${JSON.stringify(a)} != ${JSON.stringify(e)}`;
    }
    if (Array.isArray(a) !== Array.isArray(e)) return `${path}: ${JSON.stringify(a)} != ${JSON.stringify(e)}`;
    if (Array.isArray(a) && Array.isArray(e)) {
      if (a.length !== e.length) return `${path}: length ${a.length} != ${e.length}`;
      for (let i = 0; i < a.length; i++) {
        const d = walk(a[i]!, e[i]!, `${path}[${i}]`);
        if (d) return d;
      }
      return null;
    }
    const ao = a as Record<string, Encoded>;
    const eo = e as Record<string, Encoded>;
    const keys = new Set([...Object.keys(ao), ...Object.keys(eo)]);
    for (const key of keys) {
      if (!(key in ao) || !(key in eo)) return `${path}.${key}: missing on ${key in ao ? 'Python' : 'TypeScript'} side`;
      const d = walk(ao[key]!, eo[key]!, `${path}.${key}`);
      if (d) return d;
    }
    return null;
  };
  return walk(canonical(actual), canonical(expected), '$');
}
