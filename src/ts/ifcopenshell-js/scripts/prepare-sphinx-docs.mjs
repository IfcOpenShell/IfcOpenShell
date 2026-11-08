// This file was generated with the assistance of an AI coding tool.
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { basename, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const output = fileURLToPath(new URL('../../../../docs/output/typescript-api/', import.meta.url));
const label = (file, anchor) => `typescript-${basename(file, '.md').toLowerCase()}-${anchor}`;

// Give TypeDoc's member anchors Sphinx targets, unique across modules. This
// lets MyST resolve both local and cross-module links to the generated HTML.
for (const file of readdirSync(output).filter((file) => file.endsWith('.md'))) {
  const path = join(output, file);
  const source = readFileSync(path, 'utf8')
    .replace(/<a id="([^"]+)"><\/a>/g, (_, anchor) => `(${label(file, anchor)})=\n`)
    .replace(/\]\(([^()\s]*\.md)?#([^()\s]+)\)/g, (_, target, anchor) =>
      `](#${label(target ?? file, anchor)})`,
    );
  writeFileSync(path, source);
}
