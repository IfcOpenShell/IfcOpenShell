// This file was generated with the assistance of an AI coding tool.

import { spawn } from 'node:child_process';
import { readdirSync } from 'node:fs';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { expect, it } from 'vitest';
import { describeOrSkip } from './_helper.js';

const packageRoot = fileURLToPath(new URL('..', import.meta.url));
const repoRoot = resolve(packageRoot, '../../..');
const docsRoot = resolve(repoRoot, 'docs/ifcopenshell/examples');
const helloWorld = resolve(docsRoot, 'models/hello_world.ifc');
const fzkHaus = resolve(docsRoot, 'models/AC20-FZK-Haus.ifc');
const loader = pathToFileURL(resolve(packageRoot, 'tests/doc-example-register.mjs')).href;

// geometry_tree needs the OpenCASCADE tree plugins, which not every WASM build
// has, so it is not run here.
const groups = [
  { dir: 'hello_world', model: helloWorld },
  { dir: 'code_examples', model: helloWorld },
  { dir: 'geometry_processing', model: fzkHaus },
  { dir: 'geometry_creation', model: helloWorld },
  { dir: 'schema_querying', model: helloWorld },
];

const examples = groups.flatMap(({ dir, model }) => (
  readdirSync(resolve(docsRoot, dir))
    .filter((name) => name.endsWith('.mjs') && !name.startsWith('_'))
    .sort()
    .map((name) => ({ script: `${dir}/${name}`, model }))
));

function runExample(script: string, model: string, cwd: string): Promise<number> {
  return new Promise((resolveExit, reject) => {
    const child = spawn(process.execPath, ['--import', loader, script, model], {
      cwd,
      env: process.env,
      stdio: 'inherit',
    });
    child.on('error', reject);
    child.on('exit', (code) => resolveExit(code ?? 1));
  });
}

describeOrSkip('documentation examples', () => {
  it.each(examples)('$script', async ({ script, model }) => {
    const cwd = await mkdtemp(join(tmpdir(), 'ifcopenshell-js-doc-'));
    try {
      const code = await runExample(resolve(docsRoot, script), model, cwd);
      expect(code).toBe(0);
    } finally {
      await rm(cwd, { recursive: true, force: true });
    }
  });
});
