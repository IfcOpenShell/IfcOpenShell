
/** RGB triplet with components normalized to the `[0, 1]` range. */
export type RGB = [number, number, number];

/** Minimum brightness floor and maximum lift applied to hashed colors. */
const HASH_MIN = 0.25;
const HASH_SPAN = 0.55;

/**
 * Generate a deterministic RGB color from a string hash.
 *
 * Uses an FNV-1a style hash so that the same input always maps to the same
 * color — handy for assigning consistent display colors to IFC entity
 * types (e.g. `hashColor('IfcWall')`).
 *
 * Components are returned in the `[0, 1]` range and deliberately biased
 * away from pure black / pure white so they remain visible on both light
 * and dark backgrounds.
 *
 * @param input - Arbitrary string to hash.
 * @returns A deterministic `[r, g, b]` triplet in `[0, 1]`.
 */
export function hashColor(input: string): RGB {
  let h = 2166136261;
  for (let i = 0; i < input.length; i++) {
    h ^= input.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  const r = ((h >>> 0) & 0xff) / 255;
  const g = ((h >>> 8) & 0xff) / 255;
  const b = ((h >>> 16) & 0xff) / 255;
  return [HASH_MIN + HASH_SPAN * r, HASH_MIN + HASH_SPAN * g, HASH_MIN + HASH_SPAN * b];
}

/**
 * Resolve the display color for a mesh, preferring material colors
 * defined on the IFC representation over a type-based hash color.
 *
 * The `colors` buffer follows the IfcOpenShell convention: each material
 * contributes four consecutive floats (`[r, g, b, a]`), and `materialIds`
 * maps each face item to a material index. When a material color is
 * available it is used directly; otherwise the entity `type` is hashed to
 * produce a stable fallback color.
 *
 * @param type        - IFC entity type name (e.g. `'IfcWall'`).
 * @param materialIds - Per-face material indices (may be empty).
 * @param colors      - Flat RGBA material color buffer (may be empty).
 * @returns A `[r, g, b]` triplet in `[0, 1]`.
 */
export function meshColor(type: string, materialIds: ArrayLike<number>, colors: ArrayLike<number>): RGB {
  const materialId = materialIds.length > 0 ? materialIds[0]! : -1;
  const start = materialId >= 0 ? materialId * 4 : -1;
  if (start >= 0 && colors.length >= start + 3) {
    return [colors[start]!, colors[start + 1]!, colors[start + 2]!];
  }
  return hashColor(type);
}
