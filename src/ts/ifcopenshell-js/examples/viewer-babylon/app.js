// This file was generated with the assistance of an AI coding tool.
import {
  ArcRotateCamera,
  Color3,
  Color4,
  Engine,
  HemisphericLight,
  Matrix,
  Mesh,
  Scene,
  StandardMaterial,
  TransformNode,
  Vector3,
  VertexData,
} from '@babylonjs/core';
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';
import { meshColor } from 'ifcopenshell/util';

const status = document.getElementById('status');
const canvas = document.getElementById('viewport');
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

function meshToBabylon(scene, mesh, rgb, parent) {
  const data = new VertexData();
  data.positions = Array.from(mesh.vertices);
  data.indices = Array.from(mesh.faces);
  if (mesh.normals?.length) data.normals = Array.from(mesh.normals);

  const babylonMesh = new Mesh(`ifc-${mesh.id}`, scene);
  data.applyToMesh(babylonMesh);
  const material = new StandardMaterial(`mat-${mesh.id}`, scene);
  material.diffuseColor = new Color3(rgb[0], rgb[1], rgb[2]);
  babylonMesh.material = material;
  babylonMesh.setPreTransformMatrix(Matrix.FromArray(Array.from(mesh.transform)));
  babylonMesh.metadata = {
    ifcId: mesh.id,
    ifcGuid: mesh.guid,
    ifcType: mesh.type,
    ifcName: mesh.name,
  };
  babylonMesh.parent = parent;
  return babylonMesh;
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
  settings.set('weld-vertices', false);
  const iterator = new geom.Iterator(settings, model, { geometryLibrary });

  status.textContent = `Tessellating (geometryLibrary: ${geometryLibrary})…`;
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

  status.textContent = `Building Babylon scene (${meshes.length} meshes)…`;
  const engine = new Engine(canvas, true, { preserveDrawingBuffer: true, stencil: true });
  const scene = new Scene(engine);
  scene.clearColor = new Color4(0.93, 0.94, 0.97, 1);

  const camera = new ArcRotateCamera('camera', -Math.PI / 4, Math.PI / 3, 10, Vector3.Zero(), scene);
  camera.upVector = new Vector3(0, 0, 1);
  camera.attachControl(canvas, true);
  camera.wheelPrecision = 20;
  new HemisphericLight('hemi', new Vector3(0.2, 0.3, 1), scene);

  const root = new TransformNode('ifc-root', scene);
  const created = [];
  for (const mesh of meshes) {
    const rgb = meshColor(mesh.type, mesh.materialIds, mesh.colors);
    created.push(meshToBabylon(scene, mesh, rgb, root));
  }

  if (created.length) {
    let minX = Infinity;
    let minY = Infinity;
    let minZ = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    let maxZ = -Infinity;
    for (const mesh of created) {
      mesh.computeWorldMatrix(true);
      const bounds = mesh.getBoundingInfo().boundingBox;
      minX = Math.min(minX, bounds.minimumWorld.x);
      minY = Math.min(minY, bounds.minimumWorld.y);
      minZ = Math.min(minZ, bounds.minimumWorld.z);
      maxX = Math.max(maxX, bounds.maximumWorld.x);
      maxY = Math.max(maxY, bounds.maximumWorld.y);
      maxZ = Math.max(maxZ, bounds.maximumWorld.z);
    }
    root.position.set(-(minX + maxX) / 2, -(minY + maxY) / 2, -(minZ + maxZ) / 2);
    const maxDim = Math.max(maxX - minX, maxY - minY, maxZ - minZ, 1);
    camera.alpha = -Math.PI / 4;
    camera.beta = Math.PI / 3;
    camera.radius = maxDim * 1.8;
    camera.lowerRadiusLimit = maxDim * 0.05;
    camera.upperRadiusLimit = maxDim * 20;
  }

  engine.runRenderLoop(() => scene.render());
  window.addEventListener('resize', () => engine.resize());
  iterator.dispose();
  model.dispose();
  status.textContent = `Done — ${meshes.length} mesh(es)`;
}

main().catch((err) => {
  status.textContent = String(err);
  console.error(err);
});
