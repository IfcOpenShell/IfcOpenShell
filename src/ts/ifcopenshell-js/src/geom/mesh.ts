
/**
 * Pure-data description of a single triangulated mesh element.
 *
 * A {@link Mesh} carries no WASM handle — it is a detached, JS-owned snapshot
 * of one element produced by {@link GeomIterator}. The underlying WASM
 * handles used to build it are released as soon as the mesh is yielded, so
 * callers may keep and use the object freely for as long as they like.
 */
export type MeshPrecision = 'float32' | 'float64';
export type MeshFloatArray<P extends MeshPrecision> = P extends 'float64' ? Float64Array : Float32Array;

export interface Mesh<P extends MeshPrecision = 'float32'> {
  /** IFC entity ID (e.g. `42` for `#42`). */
  id: number;
  /** IFC GlobalId string of the product. */
  guid: string;
  /** IFC type name without schema prefix (e.g. `'IfcWall'`). */
  type: string;
  /** Human-readable name of the product (may be empty). */
  name: string;
  /**
   * Vertex positions as a flat `[x,y,z, x,y,z, ...]` array.
   *
   * Stored as `Float32Array` by default for direct use with WebGL buffers, or
   * as a detached `Float64Array` when the iterator requests `float64` precision.
   */
  vertices: MeshFloatArray<P>;
  /**
   * Face indices as a flat `[i0,i1,i2, i0,i1,i2, ...]` array of vertex indices.
   *
   * Stored as `Uint32Array` for direct use with Three.js / WebGL buffers.
   */
  faces: Uint32Array;
  /**
   * Vertex normals as a flat `[nx,ny,nz, ...]` array, or `null` if the
   * kernel did not produce normals.
   */
  normals: MeshFloatArray<P> | null;
  /** Edge indices as a flat buffer, when emitted by the kernel. */
  edges: Uint32Array;
  /**
   * 4×4 column-major transformation matrix placing this element in world space.
   *
   * This is a detached native column-major snapshot and can be passed directly
   * to `THREE.Matrix4.fromArray()`.
   */
  transform: Float64Array;
  /**
   * Material ID per face item of the triangulation.
   * Use this together with {@link Mesh.colors} to look up face materials.
   */
  materialIds: Int32Array;
  /** Geometry item id per face item. */
  itemIds: Int32Array;
  /** Geometry item id per edge item. */
  edgeItemIds: Int32Array;
  /** Flat UV coordinate buffer. */
  uvs: MeshFloatArray<P>;
  /**
   * Flat RGBA material colour buffer.
   *
   * Each material contributes four consecutive floats (`[r, g, b, a]`).
   * Index `i` in {@link Mesh.materialIds} refers to the colour at
   * typed-array element offset `i * 4` in this array. For `Float32Array`, the
   * corresponding byte offset is `i * 16`.
   */
  colors: MeshFloatArray<P>;
}
