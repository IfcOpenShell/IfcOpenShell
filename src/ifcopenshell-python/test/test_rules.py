import glob
import os

import pytest
import tabulate

import ifcopenshell.express.rule_executor
import ifcopenshell.validate


def pytest_generate_tests(metafunc):
    if "filename" not in metafunc.fixturenames:
        return
    rule = metafunc.config.getoption("--rule")
    filenames = [
        fn
        for fn in glob.glob(os.path.join(os.path.dirname(__file__), "fixtures/rules/*.ifc"))
        if not rule or rule in os.path.basename(fn)
    ]
    metafunc.parametrize("filename", filenames, ids=[os.path.basename(fn) for fn in filenames])


def test_file(filename):
    base = os.path.basename(filename)
    file = ifcopenshell.open(filename)
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.express.rule_executor.run(file, logger)
    results = logger.statements

    print()
    print(base)
    print()
    print(f"{len(results)} errors")

    if results:
        print(
            tabulate.tabulate(
                [[c or "" for c in r.values()] for r in results],
                maxcolwidths=[20, 100, 20],
                tablefmt="simple_grid",
                headers=results[0].keys(),
            )
        )

    if base.startswith("fail-"):
        assert len(results) > 0
    if base.startswith("pass-"):
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main(["-sx", __file__, "--import-mode=importlib"])
