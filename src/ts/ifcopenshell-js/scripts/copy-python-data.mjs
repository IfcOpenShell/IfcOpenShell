// This file was generated with the assistance of an AI coding tool.

// Data files the transpiled ifcopenshell.util opens next to itself (Pset templates, JSON tables).
import { cpSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const source = join(root, 'src', 'python', 'util');
if (existsSync(source)) {
  cpSync(source, join(root, 'dist', 'python', 'util'), { recursive: true, filter: path => !path.endsWith('.ts') });
}
