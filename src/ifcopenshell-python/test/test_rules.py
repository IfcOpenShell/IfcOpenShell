import os
import sys
import glob

import pytest
import tabulate

import ifcopenshell.validate
import ifcopenshell.express.rule_executor


@pytest.mark.parametrize(
    "filename",
    [
        fn
        for fn in glob.glob(os.path.join(os.path.dirname(__file__), "fixtures/rules/*.ifc"))
        if len(sys.argv) < 2 or sys.argv[1] in os.path.basename(fn)
    ],
)
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
    pytest.main(["-sx", __file__])
