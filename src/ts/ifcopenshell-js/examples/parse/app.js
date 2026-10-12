// This file was generated with the assistance of an AI coding tool.
import * as ifcopenshell from 'ifcopenshell';

const status = document.getElementById('status');

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

  status.textContent = 'Opening sample.ifc…';
  const response = await fetch('../sample.ifc');
  if (!response.ok) throw new Error(`Missing sample.ifc (HTTP ${response.status})`);
  const bytes = new Uint8Array(await response.arrayBuffer());

  await runtime.loadPlugin('schema', 'ifc4');
  const model = ifcopenshell.open(bytes, 'sample.ifc');
  try {
    const project = model.byType('IfcProject')[0];
    show('step-1', `Opened ${model.schema()} · project ${project?.Name ?? '(unnamed)'}`);

    const walls = model.byType('IfcWall');
    show('step-2', `Found ${walls.length} IfcWall element(s)`);

    const wall = walls[0];
    const summary = wall
      ? { id: wall.id(), type: wall.isA(), name: wall.Name, guid: wall.GlobalId }
      : null;
    show('step-3', summary ?? 'No walls in this file');

    console.log(project?.Name, model.schema());
    console.log(wall?.id(), wall?.isA(), wall?.Name, wall?.GlobalId);
    show('step-4', JSON.stringify(summary, null, 2));
    status.textContent = 'Done';
  } finally {
    model.dispose();
  }
}

main().catch((err) => {
  status.textContent = String(err);
  console.error(err);
});
