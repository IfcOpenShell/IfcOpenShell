
import { defineConfig } from 'vitest/config';
import { playwright } from '@vitest/browser-playwright';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const packageRoot = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  oxc: {
    target: 'es2022',
  },
  server: {
    fs: {
      allow: [resolve(packageRoot, '..')],
    },
  },
  test: {
    include: ['tests/browser/**/*.test.ts'],
    testTimeout: 60_000,
    hookTimeout: 60_000,
    browser: {
      enabled: true,
      provider: playwright(),
      instances: [{ browser: 'chromium' }],
    },
  },
});
