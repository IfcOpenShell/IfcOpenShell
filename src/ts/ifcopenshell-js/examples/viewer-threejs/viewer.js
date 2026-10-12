// This file was generated with the assistance of an AI coding tool.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

function createGrid() {
  const grid = new THREE.GridHelper(100, 60, 0xb7bfd0, 0xdfe3ee);
  grid.rotation.x = Math.PI / 2;
  return grid;
}

function meshToThree(mesh, rgb) {
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
  return object;
}

export function createViewer(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#eef1f6');

  const camera = new THREE.PerspectiveCamera(48, canvas.clientWidth / canvas.clientHeight, 0.1, 100000);
  camera.up.set(0, 0, 1);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;

  scene.add(new THREE.HemisphereLight(0xcde6ff, 0xe7d4be, 1.0));
  const key = new THREE.DirectionalLight(0xffffff, 1.2);
  key.position.set(12, 14, 10);
  scene.add(key);

  const grid = createGrid();
  scene.add(grid);
  const content = new THREE.Group();
  scene.add(content);

  function onResize() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
  }
  window.addEventListener('resize', onResize);

  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }
  animate();

  return {
    async streamMeshes(meshes, util) {
      let count = 0;
      for await (const mesh of meshes) {
        if (mesh.faces.length === 0 || mesh.vertices.length === 0) continue;
        content.add(meshToThree(mesh, util.meshColor(mesh.type, mesh.materialIds, mesh.colors)));
        count += 1;
      }

      const box = new THREE.Box3().setFromObject(content);
      if (!box.isEmpty()) {
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
      return count;
    },
  };
}
