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

function readSchemaIdentifier(runtime, bytes) {
  const preview = new TextDecoder().decode(bytes.slice(0, 4096));
  const stream = runtime.raw.parse.streamFromString(preview);
  if (!stream) throw new Error('Could not read the IFC header');
  let header;
  let declaration;
  try {
    header = stream.header();
    declaration = header?.fileSchema();
    const identifier = declaration?.schemaIdentifiers()?.[0];
    if (!identifier) throw new Error('FILE_SCHEMA is missing');
    return identifier;
  } finally {
    declaration?.destroy();
    header?.destroy();
    stream.destroy();
  }
}

async function main() {
  status.textContent = 'Initializing WASM…';
  const runtime = await ifcopenshell.init();

  status.textContent = 'Fetching sample…';
  const response = await fetch('../sample.ifc');
  if (!response.ok) throw new Error(`Missing sample.ifc (HTTP ${response.status})`);
  const bytes = new Uint8Array(await response.arrayBuffer());

  const schema = readSchemaIdentifier(runtime, bytes);
  show('step-1', `FILE_SCHEMA ${schema} (no schema plugin loaded yet)`);

  const pluginId = schema.toLowerCase();
  await runtime.loadPlugin('schema', pluginId);
  show('step-2', `Loaded ${runtime.loadedPlugins().join(', ')}`);

  const model = ifcopenshell.open(bytes, 'sample.ifc');
  try {
    show('step-3', `${model.schema()} · full identifier ${model.schemaIdentifier()}`);
    const products = model.byType('IfcProduct');
    const project = model.byType('IfcProject')[0];
    show(
      'step-4',
      `${products.length} IfcProduct element(s) · project ${project?.Name ?? '(unnamed)'}`,
    );
    status.textContent = 'Done';
  } finally {
    model.dispose();
  }
}

main().catch((err) => {
  status.textContent = String(err);
  console.error(err);
});
