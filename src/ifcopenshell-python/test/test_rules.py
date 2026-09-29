from pathlib import Path

import pytest
import tabulate

import ifcopenshell.express.rule_executor
import ifcopenshell.validate

from .fixture_generate import FailObj, Result, parse_result


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "filepath" not in metafunc.fixturenames:
        return
    rule = metafunc.config.getoption("--rule")
    filepaths = [fp for fp in (Path(__file__).parent / "fixtures/rules").glob("*.ifc") if not rule or rule in fp.name]
    metafunc.parametrize(
        "filepath,expected_result",
        [(fp, parse_result(fp)) for fp in filepaths],
        ids=[fp.name for fp in filepaths],
    )


def test_file(filepath: Path, expected_result: Result):
    file = ifcopenshell.open(filepath)
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.express.rule_executor.run(file, logger)
    results = logger.statements

    print()
    print(filepath.name)
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

    match expected_result:
        case FailObj(expected_count=expected_count):
            assert len(results) == expected_count
        case "pass":
            assert len(results) == 0


if __name__ == "__main__":
    pytest.main(["-sx", __file__, "--import-mode=importlib"])
