// @ts-check
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  // src/python is transpiled from Python, or its loosely typed runtime; see tsconfig.python.json.
  { ignores: ['dist/', 'src/python/'] },
  {
    files: ['src/**/*.ts'],
    extends: [eslint.configs.recommended, ...tseslint.configs.recommended, ...tseslint.configs.stylistic],
  },
);
