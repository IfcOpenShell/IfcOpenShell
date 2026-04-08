import os

import pytest

from ifcopenshell.geom.stats import StatsCollector


@pytest.mark.parametrize(
    "file",
    [os.path.join(os.path.dirname(__file__), "../../../../test/input/Allplan 2017 Test Bauteil-Oberflächen.ifc")],
)
def test_stats(file):
    collector = StatsCollector.fromFilePath(file)
    while not collector.finalized:
        collector.process()
    collector.print()
    prio = {
        "IfcWall": 2,
        "IfcBuildingElement": 1,
        "IfcBuildingElementProxy": -1,
    }
    ents = [a.name() for a in collector.includeElementTypesBasedOnBudget(prio, 1)]
    assert ents == ["IfcWall"] or ents == ["IfcWallStandardCase"]
    ents = [a.name() for a in collector.includeElementTypesBasedOnBudget(prio, 100)]
    assert "IfcBuildingElementProxy" in ents
    ents = [a.name() for a in collector.includeElementTypesBasedOnBudget(prio, 50)]
    assert "IfcBuildingElementProxy" not in ents
