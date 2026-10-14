// This file was generated with the assistance of an AI coding tool.
import * as ifcopenshell from 'ifcopenshell';

const status = document.getElementById('status');
const STD = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
const IFC = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$';

function show(stepId, value) {
  const el = document.getElementById(stepId);
  if (!el) return;
  el.textContent = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
  el.classList.add('done');
  el.closest('.lesson-step')?.classList.add('done');
}

function newGuid() {
  const hex = `0000${crypto.randomUUID().replace(/-/g, '')}`;
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < bytes.length; i++) bytes[i] = Number.parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return [...btoa(binary).slice(2)].map((char) => IFC[STD.indexOf(char)]).join('');
}

async function main() {
  status.textContent = 'Initializing WASM…';
  const runtime = await ifcopenshell.init();
  await runtime.loadPlugin('schema', 'ifc4');

  status.textContent = 'Running lesson…';
  const model = new ifcopenshell.File('IFC4');
  try {
    show('step-1', `Empty ${model.schema()} file`);

    const project = model.createEntity('IfcProject', {
      GlobalId: newGuid(),
      Name: 'Tutorial project',
    });
    const wall = model.createEntity('IfcWall', {
      GlobalId: newGuid(),
      Name: 'Tutorial wall',
    });
    show('step-2', `Created #${project.id()} IfcProject and #${wall.id()} IfcWall`);

    const walls = model.byType('IfcWall');
    console.log(project.id(), wall.Name);
    console.log(walls.length);
    show('step-3', `#${project.id()}  ${wall.Name}\n${walls.length} wall(s)`);

    const stepText = model.toString();
    console.log(stepText);
    const excerpt = stepText.length > 1200 ? `${stepText.slice(0, 1200)}\n\n… (truncated)` : stepText;
    show('step-4', excerpt);
    status.textContent = 'Done';
    window.model = model;
  } finally {
    // model.dispose();
  }
}

main().catch((err) => {
  status.textContent = String(err);
  console.error(err);
});
