
There are two ways to build pyodide ifcopenshell Python wrapper wheel.

1. Using pyodide build system (`build_pyodide.yml` does it):

- install prebuilt pyodide build and emscripten environment (see `build_pyodide.sh`)
- clone IfcOpenShell to `IfcOpenShell` folder
- create `packages/ifcopenshell` folder that will be used by pyodide build system
- from `IfcOpenShell` move building recipe `pyodide/meta.yaml` to `packages/ifcopenshell`
- run `pyodide build-recipes ifcopenshell --install`, it will
    - execute `meta.yaml` recipe - it will:
        - copy IfcOpenShell source to build folder `packages/ifcopenhell/build/ifcopenshell-0.8.0`
        - build ifcopenshell and its dependencies
        - note that rerunning `pyodide build-recipes` will remove previous build folder and rebuild all dependencies.  
        The way to avoid it, if build fails, is to use `pyodide build-recipes-no-deps ifcopenshell --continue` instead.
    - run `setup.py` in `IfcOpenShell` root, producing a wheel in `IfcOpenShell/dist`
    - copy that wheel to `packages/ifcopenshell/dist`
    - `--install` it to current build envrionment
        - copy the wheel next to `dist` folder (in root directory, next to `packages`)
        - add wheel to `dist/pyodide-lock.json`

2. Build it outside of pyodide build system.

Building inside pyodide build system should be preferred, option to build it outside is useful for debugging purposes,
since it's pure cmake without any additional moving parts.

- setup pyodide environment, see above
- clone IfcOpenShell repo next to it to `IfcOpenShell` folder
- run `python nix/build-all.py -wasm -py-313` in `IfcOpenShell`
    - it will produce Python package in `IfcOpenShell/ifcopenshell`
- run `pyodide build`
    - it will produce a wheel in `IfcOpenShell/dist`
