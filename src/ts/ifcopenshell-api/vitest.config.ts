// This file was generated with the assistance of an AI coding tool.

import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';

const local = (path: string) => fileURLToPath(new URL(path, import.meta.url));

export default defineConfig({
  resolve: {
    // Test the generated sources directly; one ifcopenshell instance is shared by all of them.
    alias: [
      { find: /^ifcopenshell$/, replacement: local('../ifcopenshell-js/dist/index.js') },
      { find: /^@ifcopenshell\/util\/(.*)$/, replacement: local('../ifcopenshell-util/src/$1.ts') },
      { find: /^@ifcopenshell\/api\/(.*)$/, replacement: local('../ifcopenshell-api/src/$1/index.ts') },
    ],
  },
  test: {
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    testTimeout: 60_000,
    hookTimeout: 60_000,
  },
  server: {
    deps: {
      inline: [/ifcopenshell/],
    },
  },
});
