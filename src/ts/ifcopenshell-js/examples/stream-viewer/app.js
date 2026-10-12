// This file was generated with the assistance of an AI coding tool.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';
import { meshColor } from 'ifcopenshell/util';

const geometryLibrary = 'manifold';
const TRACKED_TYPES = [
  'IfcWall', 'IfcSlab', 'IfcBeam', 'IfcColumn',
  'IfcWindow', 'IfcDoor', 'IfcStair', 'IfcRoof',
];

const status = document.getElementById('status');
const canvas = document.getElementById('viewport');
const logButton = document.getElementById('t-log');
let selectedEntity = null;

logButton.addEventListener('click', () => {
  if (!selectedEntity) return;
  window.selected = selectedEntity;
  console.log(selectedEntity);
});

function schemaIdentifier(runtime, bytes) {
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

function showModelPanel(model, schema) {
  const project = model.byType('IfcProject')[0];
  document.getElementById('project-name').textContent =
    `"${project?.Name ?? '(unnamed)'}" — ${schema} → ${model.schemaIdentifier()}`;

  const counts = document.getElementById('entity-counts');
  counts.replaceChildren();
  for (const type of TRACKED_TYPES) {
    const found = model.byType(type).length;
    if (!found) continue;
    const badge = document.createElement('span');
    badge.className = 'entity-badge';
    badge.append(type, ' ');
    const strong = document.createElement('strong');
    strong.textContent = String(found);
    badge.append(strong);
    counts.append(badge);
  }

  const total = model.byType('IfcProduct').length;
  document.getElementById('stream-stats').textContent = `${total} IfcProduct instances`;
  document.getElementById('stream-panel').hidden = false;
}

function formatValue(value) {
  if (value && typeof value === 'object' && typeof value.isA === 'function' && typeof value.id === 'function') {
    return `#${value.id()} ${value.isA()}`;
  }
  if (Array.isArray(value)) {
    const text = value.map(formatValue).join(', ');
    return text.length > 44 ? `${text.slice(0, 44)}…` : text;
  }
  if (value === null || value === undefined || value === '') return '—';
  const text = String(value);
  return text.length > 44 ? `${text.slice(0, 44)}…` : text;
}

function showInspector(model, object) {
  const id = object.userData.ifcId;
  const entity = model.byId(id);
  selectedEntity = entity ?? null;
  window.selected = selectedEntity;
  logButton.disabled = !selectedEntity;
  const cmd = document.getElementById('t-cmd');
  cmd.replaceChildren('entity.inspect(', Object.assign(document.createElement('span'), {
    className: 't-id',
    textContent: `#${id}`,
  }), ')');

  const output = document.getElementById('t-output');
  output.replaceChildren();
  const typeLine = document.createElement('div');
  const typeSpan = document.createElement('span');
  typeSpan.className = 't-type';
  typeSpan.textContent = entity?.isA() ?? object.userData.ifcType;
  const openBrace = document.createElement('span');
  openBrace.className = 't-brace';
  openBrace.textContent = ' {';
  typeLine.append(typeSpan, openBrace);
  output.append(typeLine);

  const info = entity ? entity.getInfo() : {
    id,
    GlobalId: object.userData.ifcGuid,
    Name: object.userData.ifcName,
  };
  const table = document.createElement('table');
  table.className = 't-table';
  for (const [key, value] of Object.entries(info)) {
    if (key === 'type') continue;
    const row = document.createElement('tr');
    for (const [className, text] of [['t-key', key], ['t-sep', ':'], ['t-val', formatValue(value)]]) {
      const cell = document.createElement('td');
      cell.className = className;
      cell.textContent = text;
      row.append(cell);
    }
    table.append(row);
  }
  output.append(table);
  const close = document.createElement('div');
  const closeBrace = document.createElement('span');
  closeBrace.className = 't-brace';
  closeBrace.textContent = '}';
  close.append(closeBrace);
  output.append(close);
  document.getElementById('terminal').hidden = false;
  document.getElementById('terminal-body').scrollTop = 0;
}

function createScene(target) {
  const renderer = new THREE.WebGLRenderer({ canvas: target, antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(target.clientWidth, target.clientHeight, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#eef1f6');
  const camera = new THREE.PerspectiveCamera(48, target.clientWidth / target.clientHeight, 0.1, 100000);
  camera.up.set(0, 0, 1);
  const controls = new OrbitControls(camera, target);
  controls.enableDamping = true;

  scene.add(new THREE.HemisphereLight(0xcde6ff, 0xe7d4be, 1.0));
  const key = new THREE.DirectionalLight(0xffffff, 1.2);
  key.position.set(12, 14, 10);
  scene.add(key);

  const grid = new THREE.GridHelper(100, 60, 0xb7bfd0, 0xdfe3ee);
  grid.rotation.x = Math.PI / 2;
  scene.add(grid);
  const content = new THREE.Group();
  scene.add(content);

  window.addEventListener('resize', () => {
    camera.aspect = target.clientWidth / target.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(target.clientWidth, target.clientHeight, false);
  });
  (function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  })();
  return { camera, controls, content, grid };
}

function addMesh(content, mesh) {
  if (!mesh.faces.length || !mesh.vertices.length) return null;
  const rgb = meshColor(mesh.type, mesh.materialIds, mesh.colors);
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(mesh.vertices, 3));
  geometry.setIndex(new THREE.BufferAttribute(mesh.faces, 1));
  if (mesh.normals?.length === mesh.vertices.length) {
    geometry.setAttribute('normal', new THREE.BufferAttribute(mesh.normals, 3));
  } else {
    geometry.computeVertexNormals();
  }
  const material = new THREE.MeshStandardMaterial({
    color: new THREE.Color(rgb[0], rgb[1], rgb[2]),
    roughness: 0.74,
    metalness: 0.06,
  });
  const object = new THREE.Mesh(geometry, material);
  object.matrix.fromArray(mesh.transform);
  object.matrixAutoUpdate = false;
  object.userData.ifcId = mesh.id;
  object.userData.ifcGuid = mesh.guid;
  object.userData.ifcType = mesh.type;
  object.userData.ifcName = mesh.name;
  content.add(object);
  return object;
}

function frameScene(camera, controls, grid, content) {
  const box = new THREE.Box3().setFromObject(content);
  if (box.isEmpty()) return;
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  content.position.copy(center).multiplyScalar(-1);
  const maxDim = Math.max(size.x, size.y, size.z, 1);
  const fov = (camera.fov * Math.PI) / 180;
  const distance = Math.max(5, (maxDim / (2 * Math.tan(fov / 2))) * 1.35);
  camera.near = Math.max(0.01, distance / 1000);
  camera.far = Math.max(1000, distance * 10);
  camera.position.set(distance, -distance, distance * 0.62);
  camera.updateProjectionMatrix();
  controls.target.set(0, 0, 0);
  controls.update();
  grid.scale.setScalar(Math.max(20, maxDim * 1.6) / 100);
  grid.position.set(0, 0, -size.z / 2 - 0.01);
}

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

async function main() {
  const { camera, controls, content, grid } = createScene(canvas);
  status.textContent = 'Initializing WASM…';
  const runtime = await ifcopenshell.init();
  status.textContent = 'Ready — open the sample to read its schema.';

  document.getElementById('file-btn').addEventListener('click', async () => {
    const fileBtn = document.getElementById('file-btn');
    const loadBtn = document.getElementById('load-btn');
    fileBtn.disabled = true;
    try {
      status.textContent = 'Reading FILE_SCHEMA…';
      const response = await fetch('../sample.ifc');
      if (!response.ok) throw new Error(`Missing sample.ifc (HTTP ${response.status})`);
      const bytes = new Uint8Array(await response.arrayBuffer());
      const schema = schemaIdentifier(runtime, bytes);
      const pluginId = schema.toLowerCase();
      await runtime.loadPlugin('schema', pluginId);
      const model = ifcopenshell.open(bytes, 'sample.ifc');
      showModelPanel(model, schema);
      status.textContent = `Schema ${schema} loaded. Click "Load geometry" to tessellate.`;
      loadBtn.hidden = false;

      loadBtn.addEventListener('click', async () => {
        loadBtn.disabled = true;
        const settings = new geom.Settings();
        let iterator;
        try {
          await runtime.loadPlugin('mapping', pluginId);
          await runtime.loadPlugin('kernel', geometryLibrary);
          settings.set('weld-vertices', false);
          status.textContent = `Tessellating (geometryLibrary: ${geometryLibrary})…`;
          iterator = new geom.Iterator(settings, model, { geometryLibrary });
          let count = 0;
          let nextYield = performance.now() + 30;
          if (iterator.initialize()) do {
            if (performance.now() >= nextYield) {
              await new Promise(requestAnimationFrame);
              nextYield = performance.now() + 30;
            }
            const data = readMesh(iterator.get());
            if (!data.faces.length) continue;
            if (addMesh(content, data)) count += 1;
          } while (iterator.next());
          frameScene(camera, controls, grid, content);
          status.textContent = `Done — ${count} mesh(es). Click a mesh to inspect it.`;

          const raycaster = new THREE.Raycaster();
          const pointer = new THREE.Vector2();
          const pickTargets = [];
          content.updateMatrixWorld(true);
          content.traverse((object) => { if (object.isMesh) pickTargets.push(object); });
          canvas.addEventListener('click', (event) => {
            const rect = canvas.getBoundingClientRect();
            pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
            raycaster.setFromCamera(pointer, camera);
            const hits = raycaster.intersectObjects(pickTargets, false);
            if (hits.length) showInspector(model, hits[0].object);
          });
        } catch (error) {
          status.textContent = String(error);
          console.error(error);
          loadBtn.disabled = false;
        } finally {
          iterator?.dispose();
        }
      }, { once: true });
    } catch (error) {
      status.textContent = String(error);
      console.error(error);
      fileBtn.disabled = false;
    }
  }, { once: true });
}

main().catch((err) => {
  status.textContent = String(err);
  console.error(err);
});
