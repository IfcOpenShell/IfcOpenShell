/** A renderer-neutral three-dimensional point. */
export type MatrixPoint3 = readonly [number, number, number];

/** Convert a 16-element row-major matrix to column-major storage. */
export function rowMajorToColumnMajor4(matrix: ArrayLike<number>): Float64Array {
  return transposeMatrix4(matrix, 'row-major');
}

/** Convert a 16-element column-major matrix to row-major storage. */
export function columnMajorToRowMajor4(matrix: ArrayLike<number>): Float64Array {
  return transposeMatrix4(matrix, 'column-major');
}

/** Transform a point with a 16-element column-major affine/projective matrix. */
export function transformPoint4(matrix: ArrayLike<number>, point: MatrixPoint3): [number, number, number] {
  validateMatrix4(matrix, 'column-major');
  const [x, y, z] = point;
  const w = matrix[3]! * x + matrix[7]! * y + matrix[11]! * z + matrix[15]!;
  if (w === 0) throw new RangeError('Cannot transform a point whose homogeneous coordinate is zero');
  const divisor = w === 1 ? 1 : w;
  return [
    (matrix[0]! * x + matrix[4]! * y + matrix[8]! * z + matrix[12]!) / divisor,
    (matrix[1]! * x + matrix[5]! * y + matrix[9]! * z + matrix[13]!) / divisor,
    (matrix[2]! * x + matrix[6]! * y + matrix[10]! * z + matrix[14]!) / divisor,
  ];
}

function transposeMatrix4(matrix: ArrayLike<number>, layout: string): Float64Array {
  validateMatrix4(matrix, layout);
  return new Float64Array([
    matrix[0]!, matrix[4]!, matrix[8]!, matrix[12]!,
    matrix[1]!, matrix[5]!, matrix[9]!, matrix[13]!,
    matrix[2]!, matrix[6]!, matrix[10]!, matrix[14]!,
    matrix[3]!, matrix[7]!, matrix[11]!, matrix[15]!,
  ]);
}

function validateMatrix4(matrix: ArrayLike<number>, layout: string): void {
  if (matrix.length !== 16) {
    throw new RangeError(`Expected a 16-element ${layout} Matrix4, received ${matrix.length}`);
  }
}
