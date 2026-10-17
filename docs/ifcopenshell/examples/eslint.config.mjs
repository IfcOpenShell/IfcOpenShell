// This file was generated with the assistance of an AI coding tool.
//
// Lints the programs that the manual includes snippets from. It has no imports
// so that it can be run by the ESLint of src/ts/ifcopenshell-js:
//
//   cd src/ts/ifcopenshell-js
//   npm run lint:docs

export default [
  // Scratch programs, which no page includes.
  { ignores: ['**/_*.mjs'] },
  {
    files: ['**/*.mjs'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: { console: 'readonly', process: 'readonly' },
    },
    rules: {
      'no-undef': 'error',
      'no-unused-vars': 'error',
      curly: ['error', 'all'],
      eqeqeq: 'error',
      // Longer lines scroll horizontally in the manual's code blocks.
      'max-len': ['error', { code: 80 }],
      'max-statements-per-line': ['error', { max: 1 }],
      'no-nested-ternary': 'error',
      'object-shorthand': 'error',
      'prefer-const': 'error',
    },
  },
];
