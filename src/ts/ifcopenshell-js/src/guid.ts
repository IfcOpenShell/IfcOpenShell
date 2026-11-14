// This file was generated with the assistance of an AI coding tool.

/**
 * IFC GlobalId helpers, as in Python `ifcopenshell.guid`.
 *
 * @module Guid
 */

const STANDARD = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
const IFC = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$';

function translate(text: string, from: string, to: string): string {
  return Array.from(text, c => to[from.indexOf(c)] ?? c).join('');
}

/** Convert a hex-encoded UUID to a 22-character IFC GlobalId. */
export function compress(uuid: string): string {
  const hex = '0000' + uuid.toLowerCase().replace(/\W/g, '');
  const bytes = hex.match(/../g)!.map(pair => String.fromCharCode(parseInt(pair, 16))).join('');
  return translate(btoa(bytes).slice(2), STANDARD, IFC);
}

/** Convert a 22-character IFC GlobalId to a hex-encoded UUID. */
export function expand(guid: string): string {
  const bytes = atob('AA' + translate(guid, IFC, STANDARD));
  return Array.from(bytes, c => c.charCodeAt(0).toString(16).padStart(2, '0')).join('').slice(4);
}

/** Format a hex UUID as `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`. */
export function split(uuid: string): string {
  return [uuid.slice(0, 8), uuid.slice(8, 12), uuid.slice(12, 16), uuid.slice(16, 20), uuid.slice(20)].join('-');
}

/** Generate a random IFC GlobalId. */
function newGuid(): string {
  return compress(crypto.randomUUID());
}

export { newGuid as new };
