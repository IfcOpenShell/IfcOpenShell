<!-- This file was generated with the assistance of an AI coding tool. -->

# Parity tests

Checks the generated `@ifcopenshell/util` and `@ifcopenshell/api` against Python
by replaying the calls the Python test suite makes. See the L3 section of
[PLAN.md](../PLAN.md) for the design.

`record.py` writes `golden/<module>.json` (not committed); the tests of
`src/ts/ifcopenshell-util` and `src/ts/ifcopenshell-api` replay them. How to run both is
described in "Running the tests" in [../README.md](../README.md); in short, from either
package folder:

```shell
npm run generate    # transpile into ../ifcopenshell-util/src and ../ifcopenshell-api/src
npm run record      # run the package's Python tests, write golden/*.json (needs pytest and ifcopenshell)
npm test            # replay against the generated sources (needs IFCOPENSHELL_WASM_DIR)
```

`record.py` records the modules in its `DEFAULT_MODULES` by default; `util` or `api`
records that package's defaults. Pass module names to record others, for example
`python src/transpiler/parity/record.py util.pset api.attribute`. Each
recorded module is loaded from this checkout's source, and its Python tests
come from `src/ifcopenshell-python/test/{util,api}`.

Replay skips a call, giving the reason, if its Python test failed, its function
is a stub, or its file did not transpile. Skipped calls therefore show what is
still to be ported.
