# ifctester

## Web app
The IfcTester web app is written in Svelte 5, and uses Pyodide to run IfcOpenShell and the `ifctester` library in the browser.

### Development
```
make webapp-dev
```

The above command loads the latest `ifctester` wheel from PyPi repository. If you want to build and use a local ifctester wheel instead:
```
make ifctester-wheel  # Build and copy the wheel to the correct location
make webapp-dev IFCTESTER_INSTALL_SOURCE=wheel
```

### Production build
```
make webapp-build
```

Or, build and use a local ifctester wheel:
```
make ifctester-wheel
make webapp-build IFCTESTER_INSTALL_SOURCE=wheel
```

Notes:
- Pyodide and required bundled wheels are downloaded to `webapp/public/pyodide` on first build and re-used for later builds.
- If you want to explicitly set a wheel URL, pass `IFCTESTER_WHEEL_URL=/worker/bin/<wheel-name>.whl` to the make command.
