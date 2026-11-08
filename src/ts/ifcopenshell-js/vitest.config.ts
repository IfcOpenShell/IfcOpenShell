import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    exclude: ['tests/browser/**/*.test.ts'],
    testTimeout: 60_000,
    hookTimeout: 60_000,
  },
  server: {
    deps: {
      inline: [/ifcopenshell/],
    },
  },
});
