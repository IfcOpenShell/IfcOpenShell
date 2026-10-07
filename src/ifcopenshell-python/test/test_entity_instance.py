# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import json
import subprocess
import sys

import pytest

import ifcopenshell
import test.bootstrap

BOUNDARY_CYCLE = """
import sys; sys.path[:] = [p for p in sys.path if p]
import json
import ifcopenshell

files = []

def boundaries(names, last_refers_to=0):
    f = ifcopenshell.file(schema="IFC4")
    files.append(f)
    instances = [f.create_entity("IfcRelSpaceBoundary2ndLevel", GlobalId=name, Name=name) for name in names]
    for boundary, corresponding in zip(instances, instances[1:]):
        boundary.CorrespondingBoundary = corresponding
    instances[-1].CorrespondingBoundary = instances[last_refers_to]
    return instances

"""


def run_isolated(script):
    result = subprocess.run([sys.executable, "-c", BOUNDARY_CYCLE + script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr or result.stdout
    return json.loads(result.stdout)


class TestGetInfo2(test.bootstrap.IFC4):
    def test_instance_attribute(self):
        brep = self.file.create_entity("IfcFacetedBrep")
        shell = self.file.create_entity("IfcClosedShell")
        brep.Outer = shell
        assert brep.get_info(recursive=True) == {
            "Outer": {"CfsFaces": None, "id": 2, "type": "IfcClosedShell"},
            "id": 1,
            "type": "IfcFacetedBrep",
        }

    def test_aggregate_of_instance_attribute(self):
        shell = self.file.create_entity("IfcClosedShell")
        faces = [self.file.create_entity("IfcFace") for i in range(3)]
        shell.CfsFaces = faces
        assert shell.get_info(recursive=True)["CfsFaces"] == (
            {"Bounds": None, "id": 2, "type": "IfcFace"},
            {"Bounds": None, "id": 3, "type": "IfcFace"},
            {"Bounds": None, "id": 4, "type": "IfcFace"},
        )

    def test_aggregate_of_aggregate_of_instance_attribute(self):
        surface = self.file.create_entity("IfcBSplineSurfaceWithKnots")
        pp = [self.file.create_entity("IfcCartesianPoint", [float(i)]) for i in range(4)]
        surface.ControlPointsList = [pp[:2], pp[2:]]
        assert surface.get_info(recursive=True)["ControlPointsList"] == (
            (
                {"Coordinates": (0.0,), "id": 2, "type": "IfcCartesianPoint"},
                {"Coordinates": (1.0,), "id": 3, "type": "IfcCartesianPoint"},
            ),
            (
                {"Coordinates": (2.0,), "id": 4, "type": "IfcCartesianPoint"},
                {"Coordinates": (3.0,), "id": 5, "type": "IfcCartesianPoint"},
            ),
        )

    def test_exclude_identifier(self):
        brep = self.file.create_entity("IfcFacetedBrep")
        shell = self.file.create_entity("IfcClosedShell")
        brep.Outer = shell
        assert brep.get_info(recursive=True, include_identifier=False) == {
            "Outer": {"CfsFaces": None, "type": "IfcClosedShell"},
            "type": "IfcFacetedBrep",
        }

    def test_cycle(self):
        info = run_isolated("a, b = boundaries('AB'); print(json.dumps(a.get_info(recursive=True)))")
        assert (info["id"], info["Name"]) == (1, "A")
        assert (info["CorrespondingBoundary"]["id"], info["CorrespondingBoundary"]["Name"]) == (2, "B")
        assert info["CorrespondingBoundary"]["CorrespondingBoundary"] == {
            "id": 1,
            "type": "IfcRelSpaceBoundary2ndLevel",
            "_CYCLE": 2,
        }

    def test_cycle_exclude_identifier(self):
        info = run_isolated(
            "a, b = boundaries('AB'); print(json.dumps(a.get_info(recursive=True, include_identifier=False)))"
        )
        assert info["CorrespondingBoundary"]["CorrespondingBoundary"] == {
            "type": "IfcRelSpaceBoundary2ndLevel",
            "_CYCLE": 2,
        }

    def test_cycle_self_reference(self):
        info = run_isolated("(a,) = boundaries('A'); print(json.dumps(a.get_info(recursive=True)))")
        assert info["CorrespondingBoundary"] == {"id": 1, "type": "IfcRelSpaceBoundary2ndLevel", "_CYCLE": 1}

    def test_cycle_python_fallback(self):
        infos = run_isolated(
            "a, b, c = boundaries('ABC', last_refers_to=1);"
            "print(json.dumps([a.get_info(recursive=True), a.get_info_py(recursive=True),"
            "a.get_info(recursive=True, ignore=('Description',))]))"
        )
        assert infos[0]["CorrespondingBoundary"]["CorrespondingBoundary"]["CorrespondingBoundary"] == {
            "id": 2,
            "type": "IfcRelSpaceBoundary2ndLevel",
            "_CYCLE": 2,
        }
        assert infos[1] == infos[0]
        assert infos[2]["CorrespondingBoundary"]["CorrespondingBoundary"]["CorrespondingBoundary"] == {
            "id": 2,
            "type": "IfcRelSpaceBoundary2ndLevel",
            "_CYCLE": 2,
        }

    def test_shared_instance_is_not_a_cycle(self):
        sphere = self.file.create_entity("IfcSphere", Radius=1.0)
        sphere.Position = self.file.create_entity("IfcAxis2Placement3D")
        result = self.file.create_entity("IfcBooleanResult", "UNION", sphere, sphere)
        expanded = {
            "Position": {"Location": None, "Axis": None, "RefDirection": None, "id": 2, "type": "IfcAxis2Placement3D"},
            "Radius": 1.0,
            "id": 1,
            "type": "IfcSphere",
        }
        for info in (result.get_info(recursive=True), result.get_info_py(recursive=True)):
            assert info["FirstOperand"] == expanded
            assert info["SecondOperand"] == expanded


def test_equality():
    f = ifcopenshell.file()
    g = ifcopenshell.file()
    f.createIfcCartesianPoint((0.0, 0.0))
    g.createIfcCartesianPoint((0.0, 0.0))
    assert f[1] == g[1]
    g[1].Coordinates = (1.0, 0.0)
    assert f[1] != g[1]
    f.createIfcCartesianPoint((0.0, 0.0))
    assert f[1] == f[1]
    assert f[1] != f[2]


def test_equality_of_cycles():
    assert run_isolated(
        "a = boundaries('AB')[0];"
        "same = boundaries('AB')[0];"
        "renamed = boundaries('AC')[0];"
        "other_target = boundaries('AB', last_refers_to=1)[0];"
        "print(json.dumps([a == same, a != same, a == renamed, a == other_target]))"
    ) == [True, False, False, False]


def test_equality_of_cycles_by_value_in_one_file():
    assert run_isolated(
        "a, b = boundaries('AB');"
        "c, d = [a.file.create_entity('IfcRelSpaceBoundary2ndLevel', GlobalId=name, Name=name) for name in 'AB'];"
        "c.CorrespondingBoundary = d; d.CorrespondingBoundary = c;"
        "ifcopenshell.settings.compare_instances_by_value = True;"
        "print(json.dumps([a == c, a == b]))"
    ) == [True, False]


def test_equality_of_owning_file():
    f = ifcopenshell.file()
    g = ifcopenshell.file()
    f.createIfcCartesianPoint((0.0, 0.0))
    f.createIfcCartesianPoint((0.0, 0.0))
    g.createIfcCartesianPoint((0.0, 0.0))
    assert f[1].file == f[1].file
    assert f[1].file == f[2].file
    assert f[1].file != g[1].file


def test_setting_logical():
    f = ifcopenshell.file()
    inst = f.createIfcPresentationLayerWithStyle(LayerOn="UNKNOWN")
    assert inst.LayerOn == "UNKNOWN"
    assert ".U." in str(inst)
    with pytest.raises(Exception):
        inst.LayerOn = "SOME_OTHER_STRING"
    inst.LayerOn = False
    assert inst.LayerOn is False
    assert ".F." in str(inst)
    inst.LayerOn = True
    assert inst.LayerOn is True
    assert ".T." in str(inst)
