import { entity_instance, type AttributeValueType } from '../entity_instance.js';
import type { file } from '../file.js';

export interface AttributeEntry { name: string; value: string; }
export interface entity_instance_info {
  id: number;
  type: string;
  guid: string | null;
  attributes: AttributeEntry[];
}

export function formatAttributeValue(value: AttributeValueType): string {
  if (value === null) return '$';
  if (value instanceof entity_instance) return `#${value.id()} - ${value.isA()}`;
  if (Array.isArray(value)) return `[${value.map(formatAttributeValue).join(', ')}]`;
  return String(value);
}

function release(value: AttributeValueType): void {
  if (value instanceof entity_instance) value.dispose();
  else if (Array.isArray(value)) value.forEach(release);
}

export async function inspectEntity(file: file, id: number): Promise<entity_instance_info | null> {
  using entity = file.get(id);
  if (!entity) return null;
  const attributes = entity.attributes().map(name => {
    const value = entity.get(name);
    try { return { name, value: formatAttributeValue(value) }; } finally { release(value); }
  });
  const guid = attributes.some(item => item.name === 'GlobalId') ? entity.get('GlobalId') : null;
  return { id: entity.id(), type: entity.isA(), guid: typeof guid === 'string' ? guid : null, attributes };
}
