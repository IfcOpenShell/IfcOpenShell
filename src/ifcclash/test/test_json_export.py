# This file was generated with the assistance of an AI coding tool.
# SPDX-License-Identifier: LGPL-3.0-or-later
from __future__ import annotations

import copy
import json
import logging

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.guid
import numpy as np

from ifcclash import ifcclash


def export_report(path, report, sort_keys=False):
    settings = ifcclash.ClashSettings()
    settings.output = str(path)
    settings.sort_json_keys = sort_keys
    settings.logger = logging.getLogger("ifcclash.test")
    clasher = ifcclash.Clasher(settings)
    clasher.clash_sets = copy.deepcopy(report)
    clasher.export_json()
    return path.read_bytes()


def reverse_objects(value):
    if isinstance(value, dict):
        return {key: reverse_objects(item) for key, item in reversed(value.items())}
    if isinstance(value, list):
        return [reverse_objects(item) for item in value]
    return value


def numeric_tokens(data):
    return json.loads(data, parse_int=lambda s: ("int", s), parse_float=lambda s: ("float", s))


def report_fixture():
    directed = {
        "a_global_id": "0000000000000000000001",
        "b_global_id": "0000000000000000000002",
        "a_ifc_class": "IfcWall",
        "b_ifc_class": "IfcSlab",
        "a_name": "Wall Ω",
        "b_name": "Slab",
        "type": "collision",
        "p1": [-0.0, 1e-20, 1.2345678901234567],
        "p2": [3.0, 2.0, 1.0],
        "distance": 0.125,
        "smart_group": 9007199254740993,
        "extra": {"z": None, "a": [True, False, "1"]},
    }
    opposite = copy.deepcopy(directed)
    opposite.update(
        a_global_id=directed["b_global_id"], b_global_id=directed["a_global_id"], p1=directed["p2"], p2=directed["p1"]
    )
    clashes = {
        opposite["a_global_id"] + "-" + opposite["b_global_id"]: opposite,
        directed["a_global_id"] + "-" + directed["b_global_id"]: directed,
    }
    report = [{"name": "Z first", "a": [], "b": [], "mode": "collision", "clashes": clashes}]
    report.append(copy.deepcopy(report[0]))
    report[1]["name"] = "A second"
    return report


def test_stable_json_preserves_the_complete_report(tmp_path):
    report = report_fixture()
    legacy = export_report(tmp_path / "legacy.json", report)
    first = export_report(tmp_path / "first.json", report, sort_keys=True)
    second = export_report(tmp_path / "second.json", reverse_objects(report), sort_keys=True)
    assert first == second
    # Compare every field and the original numeric tokens, including -0.0 and
    # the large integer. Directed pairs, p1/p2 and all list positions survive.
    assert numeric_tokens(first) == numeric_tokens(legacy)
    assert len(json.loads(first)[0]["clashes"]) == 2
    assert [item["name"] for item in json.loads(first)] == ["Z first", "A second"]


def test_default_json_keeps_existing_serialization(tmp_path):
    report = report_fixture()
    assert export_report(tmp_path / "default.json", report) == json.dumps(report, indent=4).encode("utf-8")


def write_movement_fixture(path, moved):
    model = ifcopenshell.api.project.create_file(version="IFC4")
    project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name="Clash ordering fixture")
    project.GlobalId = ifcopenshell.guid.compress(f"{100:032x}")
    unit = ifcopenshell.api.unit.add_si_unit(model, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(model, units=[unit])
    context = ifcopenshell.api.context.add_context(model, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
    )
    for index, position in enumerate([(0.0, 0.0, 0.0), (0.5, 0.2, 0.2), (0.8 + 3.0 * moved, 0.4, 0.4)]):
        element = ifcopenshell.api.root.create_entity(
            model, ifc_class="IfcWall" if index == 0 else "IfcBuildingElementProxy", name=f"Box {index}"
        )
        element.GlobalId = ifcopenshell.guid.compress(f"{index + 1:032x}")
        representation = ifcopenshell.api.geometry.add_wall_representation(
            model, context=body, length=1.0, height=1.0, thickness=1.0
        )
        ifcopenshell.api.geometry.assign_representation(model, product=element, representation=representation)
        matrix = np.eye(4)
        matrix[:3, 3] = position
        ifcopenshell.api.geometry.edit_object_placement(model, product=element, matrix=matrix)
    model.header.file_name.time_stamp = "2000-01-01T00:00:00"
    model.header.file_name.author = ()
    model.header.file_name.organization = ()
    model.write(str(path))


def test_full_native_report_is_repeatable_for_a_movement(tmp_path, monkeypatch):
    monkeypatch.setattr(ifcclash.multiprocessing, "cpu_count", lambda: 1)
    counts = []
    for moved in (False, True):
        source = tmp_path / ("moved.ifc" if moved else "base.ifc")
        write_movement_fixture(source, moved)
        reports = []
        for repeat in range(2):
            settings = ifcclash.ClashSettings()
            settings.output = str(tmp_path / f"{moved}-{repeat}.json")
            settings.sort_json_keys = True
            settings.logger = logging.getLogger("ifcclash.test")
            clasher = ifcclash.Clasher(settings)
            clasher.clash_sets = [
                {
                    "name": "Wall against movable boxes",
                    "a": [{"file": str(source), "mode": "i", "selector": "IfcWall"}],
                    "b": [{"file": str(source), "mode": "i", "selector": "IfcBuildingElementProxy"}],
                    "mode": "intersection",
                    "tolerance": 0.002,
                    "check_all": True,
                }
            ]
            clasher.clash()
            # Capture all public output before the writer strips its runtime IFC handles.
            expected = copy.deepcopy(clasher.clash_sets, {id(model): model for model in clasher.ifcs.values()})
            for group in ("a", "b"):
                for item in expected[0][group]:
                    del item["ifc"]
            clasher.export()
            result = (tmp_path / f"{moved}-{repeat}.json").read_bytes()
            assert numeric_tokens(result) == numeric_tokens(json.dumps(expected))
            reports.append(result)
        assert reports[0] == reports[1]
        counts.append(len(json.loads(reports[0])[0]["clashes"]))
    assert counts == [2, 1]
