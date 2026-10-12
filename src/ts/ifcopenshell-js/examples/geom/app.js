// This file was generated with the assistance of an AI coding tool.
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';

const status = document.getElementById('status');
const geometryLibrary = 'manifold';

function show(stepId, value) {
  const el = document.getElementById(stepId);
  if (!el) return;
  el.textContent = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
  el.classList.add('done');
  el.closest('.lesson-step')?.classList.add('done');
}

function readMesh(shape) {
  const tri = shape.asTriangulationElement();
  const nativeGeometry = tri.geometry();
  try {
    return {
      type: shape.type(),
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

async function main() {
  status.textContent = 'Initializing WASM…';
  const runtime = await ifcopenshell.init();

  status.textContent = 'Opening sample.ifc…';
  const response = await fetch('../sample.ifc');
  if (!response.ok) throw new Error(`Missing sample.ifc (HTTP ${response.status})`);
  const bytes = new Uint8Array(await response.arrayBuffer());

  await runtime.loadPlugin('schema', 'ifc4');
  await runtime.loadPlugin('mapping', 'ifc4');
  await runtime.loadPlugin('kernel', geometryLibrary);
  const model = ifcopenshell.open(bytes, 'sample.ifc');
  const settings = new geom.Settings();
  let iterator;
  try {
    settings.set('weld-vertices', false);
    show('step-1', 'Settings ready (weld-vertices false)');

    iterator = new geom.Iterator(settings, model, { geometryLibrary });
    show('step-2', `Iterator created (geometryLibrary: ${geometryLibrary})`);

    const meshes = [];
    let nextYield = performance.now() + 30;
    if (iterator.initialize()) do {
      if (performance.now() >= nextYield) {
        await new Promise(requestAnimationFrame);
        nextYield = performance.now() + 30;
      }
      const data = readMesh(iterator.get());
      if (!data.faces.length) continue;
      meshes.push(data);
    } while (iterator.next());
    show('step-3', `Collected ${meshes.length} mesh(es)`);

    const mesh = meshes[0];
    if (mesh) {
      const vertices = mesh.vertices.length / 3;
      const triangles = mesh.faces.length / 3;
      console.log(mesh.type, vertices, triangles);
      show('step-4', `${mesh.type}  ${vertices} vertices  ${triangles} triangles`);
    } else {
      show('step-4', 'No meshes collected');
    }
    status.textContent = 'Done';
  } finally {
    iterator?.dispose();
    model.dispose();
  }
}

main().catch((err) => {
  status.textContent = String(err);
  console.error(err);
});
