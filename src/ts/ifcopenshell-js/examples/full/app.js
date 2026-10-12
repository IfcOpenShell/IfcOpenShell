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

async function main() {
  status.textContent = 'Initializing WASM…';
  const runtime = await ifcopenshell.init();

  status.textContent = 'Running lesson…';
  const response = await fetch('../sample.ifc');
  if (!response.ok) throw new Error(`Missing sample.ifc (HTTP ${response.status})`);
  const bytes = new Uint8Array(await response.arrayBuffer());

  await runtime.loadPlugin('schema', 'ifc4');
  const model = ifcopenshell.open(bytes, 'sample.ifc');
  const settings = new geom.Settings();
  let iterator;
  try {
    const project = model.byType('IfcProject')[0];
    show('step-1', `Opened ${model.schema()} · project ${project?.Name ?? '(unnamed)'}`);

    const walls = model.byType('IfcWall');
    let edited = null;
    if (walls.length > 0) {
      const previous = walls[0].Name ?? null;
      walls[0].Name = 'Edited in full example';
      edited = { id: walls[0].id(), previous, name: walls[0].Name };
    }
    show('step-2', edited ? `#${edited.id}: "${edited.previous}" → "${edited.name}"` : 'No walls to edit');

    await runtime.loadPlugin('mapping', 'ifc4');
    await runtime.loadPlugin('kernel', geometryLibrary);
    settings.set('weld-vertices', false);
    iterator = new geom.Iterator(settings, model, { geometryLibrary });

    let meshes = 0;
    let nextYield = performance.now() + 30;
    if (iterator.initialize()) do {
      if (performance.now() >= nextYield) {
        await new Promise(requestAnimationFrame);
        nextYield = performance.now() + 30;
      }
      const shape = iterator.get();
      const tri = shape.asTriangulationElement();
      const nativeGeometry = tri.geometry();
      let faces;
      try {
        faces = nativeGeometry.facesBuffer(Uint32Array);
      } finally {
        nativeGeometry.destroy();
        tri.destroy();
        shape.destroy();
      }
      if (!faces.length) continue;
      meshes += 1;
    } while (iterator.next());
    show('step-3', `Collected ${meshes} mesh(es)`);

    const name = walls[0]?.Name ?? '(no wall)';
    console.log(name, meshes);
    show('step-4', `${name}  ${meshes}`);
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
