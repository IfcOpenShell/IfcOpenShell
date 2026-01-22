# ifctester

## Web app
The IfcTester web app is written in Svelte 5, and uses Pyodide to run IfcOpenShell and the `ifctester` library in the browser.

### Development
```
make webapp-dev
```

The web app uses a bundled `ifctester-*.whl` from `webapp/public/worker/bin` by default. If you want to build and use a local ifctester wheel instead:
```
make ifctester-wheel  # Builds and copies the wheel into bin
make webapp-dev IFCTESTER_WHEEL_URL=/worker/bin/<wheel-name>.whl
```

### Building for Production
```
make webapp-build
```

Or, build and use a local ifctester wheel:
```
make ifctester-wheel
make webapp-build IFCTESTER_WHEEL_URL=/worker/bin/<wheel-name>.whl
```

### Updating the bundled ifctester wheel
1) Build a fresh wheel:
```
make ifctester-wheel
```
2) Delete any older `ifctester-*.whl` files from `webapp/public/worker/bin` so only the new wheel remains.
3) Update `webapp/src/config.json` to point `wasm.ifctester_wheel_url` to the new wheel filename.
