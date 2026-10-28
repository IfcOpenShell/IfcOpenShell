<!-- This file was generated with the assistance of an AI coding tool. -->

# Parity tests

Checks the generated `@ifcopenshell/util` and `@ifcopenshell/api` against Python
by replaying the calls the Python test suite makes. See the L3 section of
[PLAN.md](../PLAN.md) for the design.

From `src/ts/ifcopenshell-parity` (run `npm install` there once):

```shell
npm run record      # run Python tests, write golden/*.json (needs pytest and ifcopenshell; not committed)
npm run generate    # transpile into ../ifcopenshell-util/src and ../ifcopenshell-api/src
npm test            # replay against the generated sources (needs IFCOPENSHELL_WASM_DIR)
npm run typecheck   # build @ifcopenshell/util and type-check @ifcopenshell/api
```

`record.py` records the modules in its `DEFAULT_MODULES` by default. Pass module names to record others, for example
`python src/transpiler/parity/record.py util.pset api.attribute`. Each
recorded module is loaded from this checkout's source, and its Python tests
come from `src/ifcopenshell-python/test/{util,api}`.

Replay skips a call, giving the reason, if its Python test failed, its function
is a stub, or its file did not transpile. Skipped calls therefore show what is
still to be ported.
