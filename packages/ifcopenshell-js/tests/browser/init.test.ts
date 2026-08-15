
import { describe, expect, it } from 'vitest';
import { init } from '../../src/index.js';

describe('browser runtime', () => {
  it('initializes the browser package and loads an IFC schema plugin', async () => {
    const shell = await init();
    try {
      await shell.loadPlugin('schema', 'ifc4');
      expect(shell.loadedPlugins()).toContain('schema:ifc4');
      const file = shell.raw.parse.newFile('IFC4', 0, '');
      expect(file).not.toBeNull();
      file?.destroy();
    } finally {
      shell.dispose();
    }
  });
});
