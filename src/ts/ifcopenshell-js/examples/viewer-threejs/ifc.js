// This file was generated with the assistance of an AI coding tool.
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';
import * as util from 'ifcopenshell/util';

export { util };

const geometryLibrary = 'manifold';

function readMesh(shape) {
  const tri = shape.asTriangulationElement();
  const nativeGeometry = tri.geometry();
  try {
    return {
      id: shape.id(),
      guid: shape.guid(),
      type: shape.type(),
      name: shape.name(),
      vertices: nativeGeometry.vertsBuffer(Float32Array),
      faces: nativeGeometry.facesBuffer(Uint32Array),
      normals: nativeGeometry.normalsBuffer(Float32Array),
      colors: nativeGeometry.colorsBuffer(Float32Array),
      materialIds: nativeGeometry.materialIdsBuffer(Int32Array),
      transform: shape.transformationBuffer(Float64Array),
    };
  } finally {
    nativeGeometry.destroy();
    tri.destroy();
    shape.destroy();
  }
}

export async function generateMeshes(filename = '../sample.ifc', setStatus = () => {}) {
  setStatus('Initializing WASM…');
  const runtime = await ifcopenshell.init();

  const name = filename.split('/').pop();
  setStatus(`Opening ${name}…`);
  const response = await fetch(filename);
  if (!response.ok) throw new Error(`Missing ${name} (HTTP ${response.status})`);
  const bytes = new Uint8Array(await response.arrayBuffer());

  await runtime.loadPlugin('schema', 'ifc4');
  await runtime.loadPlugin('mapping', 'ifc4');
  await runtime.loadPlugin('kernel', geometryLibrary);
  const model = ifcopenshell.open(bytes, name);
  const settings = new geom.Settings();
  settings.set('weld-vertices', false);

  setStatus(`Tessellating (geometryLibrary: ${geometryLibrary})…`);
  const iterator = new geom.Iterator(settings, model, { geometryLibrary });

  return {
    util,
    async *[Symbol.asyncIterator]() {
      let nextYield = performance.now() + 30;
      if (iterator.initialize()) do {
        if (performance.now() >= nextYield) {
          await new Promise(requestAnimationFrame);
          nextYield = performance.now() + 30;
        }
        const data = readMesh(iterator.get());
        if (!data.faces.length) continue;
        yield data;
      } while (iterator.next());
    },
    dispose() {
      iterator.dispose();
      model.dispose();
    },
  };
}
