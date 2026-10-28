<!-- This file was generated with the assistance of an AI coding tool. -->

# Parity tests

`record.py` runs the Python tests of the modules in its `DEFAULT_MODULES` (or the modules
given, for example `python record.py util.pset api.attribute`) and records every call the
tests make into them in `golden/<module>.json`, which is not committed.
`src/ts/ifcopenshell-js/tests/python/parity.test.ts` replays them against the transpiled
code. See "Testing" in [../PLAN.md](../PLAN.md) for the design and "Running the tests" in
[../README.md](../README.md) for how to run both.
