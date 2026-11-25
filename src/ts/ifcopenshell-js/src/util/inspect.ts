import { EntityInstance, type AttributeValueType } from '../entity_instance.js';
import type { File } from '../file.js';

export interface AttributeEntry { name: string; value: string; }
export interface EntityInspection {
  id: number;
  type: string;
  guid: string | null;
  attributes: AttributeEntry[];
}

export function formatAttributeValue(value: AttributeValueType): string {
  if (value === null) return '$';
  if (value instanceof EntityInstance) return `#${value.id()} - ${value.isA()}`;
  if (Array.isArray(value)) return `[${value.map(formatAttributeValue).join(', ')}]`;
  return String(value);
}

export async function inspectEntity(file: File, id: number): Promise<EntityInspection | null> {
  if (!file.entityNames().includes(id)) return null;
  const entity = file.byId(id);
  if (!entity) return null;
  const attributes = entity.attributes().map(name => {
    const value = entity.get(name);
    return { name, value: formatAttributeValue(value) };
  });
  const guid = attributes.some(item => item.name === 'GlobalId') ? entity.get('GlobalId') : null;
  return { id: entity.id(), type: entity.isA(), guid: typeof guid === 'string' ? guid : null, attributes };
}
