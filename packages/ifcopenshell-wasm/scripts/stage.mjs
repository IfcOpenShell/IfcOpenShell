import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { transform } from 'esbuild';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PACKAGE_ROOT = resolve(__dirname, '..');
const REPO_ROOT = resolve(PACKAGE_ROOT, '..', '..');
const DEST = join(PACKAGE_ROOT, 'wasm');

const DEFAULT_SOURCES = [
  process.env.IFCOPENSHELL_WASM_DIR,
  resolve(REPO_ROOT, 'build', 'wasm-native', 'ifcopenshell', 'full', 'ifcwrap', 'wasm'),
  resolve(REPO_ROOT, 'build', 'wasm-native', 'dist', 'full'),
  resolve(REPO_ROOT, 'build-wasm', 'ifcwrap', 'wasm'),
].filter(Boolean);

const REQUIRED = [
  'ifcopenshell_wasm.mjs',
  'ifcopenshell_wasm.node.mjs',
  'ifcopenshell_wasm.wasm',
  'ifcopenshell_api.mjs',
  'ifcopenshell_api.d.ts',
  'ifcopenshell_plugins.json',
];

function resolveSource() {
  for (const candidate of DEFAULT_SOURCES) {
    if (REQUIRED.every((name) => existsSync(join(candidate, name)))) {
      return candidate;
    }
  }
  return null;
}

function copyRequiredArtifacts(source) {
  mkdirSync(DEST, { recursive: true });
  for (const name of REQUIRED) {
    cpSync(join(source, name), join(DEST, name));
  }
  const profileMetadata = join(source, 'ifcopenshell_profile.json');
  if (existsSync(profileMetadata)) {
    cpSync(profileMetadata, join(DEST, 'ifcopenshell_profile.json'));
  }

  const manifest = JSON.parse(readFileSync(join(source, 'ifcopenshell_plugins.json'), 'utf8'));
  for (const entries of Object.values(manifest)) {
    for (const entry of Object.values(entries)) {
      const relativePath = toPosixPath(entry.wasm);
      const from = join(source, relativePath);
      if (!existsSync(from)) {
        throw new Error(`WASM plugin listed in the manifest is missing: ${from}`);
      }
      const to = join(DEST, relativePath);
      mkdirSync(dirname(to), { recursive: true });
      cpSync(from, to);
    }
  }
}

async function minifyModule(name) {
  const path = join(DEST, name);
  const source = readFileSync(path, 'utf8');
  const result = await transform(source, {
    format: 'esm',
    legalComments: 'inline',
    minify: true,
    target: 'es2022',
  });
  writeFileSync(path, result.code);
}

function toPosixPath(path) {
  return path.split('\\').join('/');
}

function writeAssetManifest() {
  const manifest = JSON.parse(readFileSync(join(DEST, 'ifcopenshell_plugins.json'), 'utf8'));
  const writeEntry = (entry) => {
    const fields = [
      `wasm: new URL(${JSON.stringify(`./wasm/${toPosixPath(entry.wasm)}`)}, import.meta.url).href`,
    ];
    if (entry.depends) {
      fields.push(`depends: ${JSON.stringify(entry.depends)}`);
    }
    return `{ ${fields.join(', ')} }`;
  };
  const lines = [
    '',
    "import initModule from './wasm/ifcopenshell_wasm.mjs';",
    "import { createIfcOpenshellModule } from './wasm/ifcopenshell_api.mjs';",
    '',
    'export { createIfcOpenshellModule, initModule };',
    "export const wasmUrl = new URL('./wasm/ifcopenshell_wasm.wasm', import.meta.url).href;",
    'export const pluginBaseUrl = import.meta.url;',
    'export const manifest = {',
  ];

  for (const [kind, entries] of Object.entries(manifest)) {
    lines.push(`  ${JSON.stringify(kind)}: {`);
    for (const [id, entry] of Object.entries(entries)) {
      lines.push(`    ${JSON.stringify(id)}: ${writeEntry(entry)},`);
    }
    lines.push('  },');
  }

  lines.push('};', '');
  writeFileSync(join(PACKAGE_ROOT, 'asset-manifest.js'), lines.join('\n'));
}

const source = resolveSource();
if (!source) {
  console.error(
    'No WASM build output found. Build the WASM target first, then rerun stage:\n' +
      '  python nix/wasm_native.py --profile full build\n' +
      'Or set IFCOPENSHELL_WASM_DIR to an existing ifcwrap/wasm directory.',
  );
  process.exit(1);
}

rmSync(DEST, { recursive: true, force: true });
copyRequiredArtifacts(source);
await Promise.all([
  minifyModule('ifcopenshell_api.mjs'),
  minifyModule('ifcopenshell_wasm.mjs'),
  minifyModule('ifcopenshell_wasm.node.mjs'),
]);
writeAssetManifest();
console.log(`Staged IfcOpenShell WASM assets from ${source} -> ${DEST}`);
