
import { AttributeValue } from '../attribute.js';
import type { IfcFile } from '../file.js';

/** A single named attribute snapshot produced by {@link inspectEntity}. */
export interface AttributeEntry {
  name: string;
  value: string;
}

/** A plain-object snapshot of an entity's metadata. */
export interface EntityInfo {
  id: number;
  type: string;
  guid: string | null;
  attributes: AttributeEntry[];
}

/** Format one attribute as a compact human-readable string. */
export async function formatAttributeValue(attr: AttributeValue): Promise<string> {
  try {
    if (attr.isNull) return '∅';
    const normalizedType = attr.type.replace(/\s+/g, '_');
    if (normalizedType === 'DERIVED') return '*';
    if (normalizedType === 'INSTANCE' || normalizedType === 'ENTITY_INSTANCE') {
      const inst = await attr.entity();
      try {
        return inst ? `#${inst.id} · ${inst.typeName}` : '$';
      } finally {
        await inst?.dispose();
      }
    }
    if (normalizedType === 'ENUM' || normalizedType === 'ENUMERATION') return await attr.string();
    if (normalizedType.startsWith('AGGREGATE') || normalizedType.includes('LIST')) {
      try {
        return `[…${await attr.size()}]`;
      } catch {
        return '[…]';
      }
    }
    try { return await attr.string(); } catch {}
    try { return String(await attr.integer()); } catch {}
    try { return String(await attr.number()); } catch {}
    try { return String(await attr.boolean()); } catch {}
    return attr.type;
  } catch {
    return '?';
  }
}

/** Inspect an entity and return its id, type, GlobalId, and formatted attributes. */
export async function inspectEntity(file: IfcFile, id: number): Promise<EntityInfo | null> {
  const entity = file.get(id);
  if (!entity) return null;
  try {
    const attributes = await Promise.all(entity.attributes().map(async (name) => {
      using attr = entity.attribute(name);
      return { name, value: await formatAttributeValue(attr) };
    }));
    let guid: string | null = null;
    if (attributes.some((item) => item.name === 'GlobalId')) {
      try {
        const value = entity.get('GlobalId');
        guid = typeof value === 'string' ? value : null;
      } catch {
        guid = null;
      }
    }
    return { id: entity.id, type: entity.type, guid, attributes };
  } finally {
    entity.dispose();
  }
}
