// This file was generated with the assistance of an AI coding tool.
import { generateMeshes } from './ifc.js';
import { createViewer } from './viewer.js';

const status = document.getElementById('status');
const canvas = document.getElementById('viewport');

async function main() {
  const viewer = createViewer(canvas);
  const meshStream = await generateMeshes('../sample.ifc', (msg) => {
    status.textContent = msg;
  });

  status.textContent = 'Streaming meshes into Three.js…';
  const count = await viewer.streamMeshes(meshStream, meshStream.util);
  meshStream.dispose();
  status.textContent = `Done — ${count} mesh(es)`;
}

main().catch((err) => {
  status.textContent = String(err);
  console.error(err);
});
