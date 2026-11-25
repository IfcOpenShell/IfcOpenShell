# This file was generated with the assistance of an AI coding tool.
import json
import os
import subprocess
import sys
import tempfile

from ifcquery.relations import relations


class TestWallRelations:
    def test_wall_has_container(self, model):
        wall = model.by_type("IfcWall")[0]
        result = relations(model, wall)
        assert result["id"] == wall.id()
        assert result["type"] == "IfcWall"
        assert result["hierarchy"]["container"]["type"] == "IfcBuildingStorey"
        assert result["hierarchy"]["container"]["name"] == "Ground Floor"

    def test_wall_has_parent(self, model):
        wall = model.by_type("IfcWall")[0]
        result = relations(model, wall)
        assert result["hierarchy"]["parent"]["type"] == "IfcBuildingStorey"

    def test_wall_no_children(self, model):
        wall = model.by_type("IfcWall")[0]
        result = relations(model, wall)
        assert "children" not in result

    def test_wall_empty_categories_omitted(self, model):
        wall = model.by_type("IfcWall")[0]
        result = relations(model, wall)
        assert "groups" not in result
        assert "systems" not in result
        assert "zones" not in result
        assert "connections" not in result
        assert "referenced_structures" not in result


class TestStoreyRelations:
    def test_storey_has_contained(self, model):
        storey = model.by_type("IfcBuildingStorey")[0]
        result = relations(model, storey)
        contained_types = {e["type"] for e in result["children"]["contained"]}
        assert "IfcWall" in contained_types
        assert "IfcSlab" in contained_types

    def test_storey_has_aggregate_parent(self, model):
        storey = model.by_type("IfcBuildingStorey")[0]
        result = relations(model, storey)
        assert result["hierarchy"]["aggregate"]["type"] == "IfcBuilding"
        assert result["hierarchy"]["aggregate"]["name"] == "TestBuilding"


class TestProjectRelations:
    def test_project_has_parts(self, model):
        project = model.by_type("IfcProject")[0]
        result = relations(model, project)
        parts = result["children"]["parts"]
        assert any(p["type"] == "IfcSite" for p in parts)

    def test_project_no_hierarchy(self, model):
        project = model.by_type("IfcProject")[0]
        result = relations(model, project)
        assert "hierarchy" not in result


class TestTraverseUp:
    def test_wall_to_project(self, model):
        wall = model.by_type("IfcWall")[0]
        chain = relations(model, wall, traverse="up")
        assert isinstance(chain, list)
        assert chain[0]["type"] == "IfcWall"
        assert chain[-1]["type"] == "IfcProject"
        types = [e["type"] for e in chain]
        assert "IfcBuildingStorey" in types
        assert "IfcBuilding" in types
        assert "IfcSite" in types

    def test_project_traverse(self, model):
        project = model.by_type("IfcProject")[0]
        chain = relations(model, project, traverse="up")
        assert len(chain) == 1
        assert chain[0]["type"] == "IfcProject"

    def test_storey_to_project(self, model):
        storey = model.by_type("IfcBuildingStorey")[0]
        chain = relations(model, storey, traverse="up")
        assert chain[0]["type"] == "IfcBuildingStorey"
        assert chain[-1]["type"] == "IfcProject"
        assert len(chain) == 4  # storey -> building -> site -> project


class TestElementsSummary:
    def test_wall_elements_includes_self(self, model):
        wall = model.by_type("IfcWall")[0]
        result = relations(model, wall)
        ids = [e["id"] for e in result["elements"]]
        assert wall.id() in ids

    def test_wall_elements_includes_container(self, model):
        wall = model.by_type("IfcWall")[0]
        result = relations(model, wall)
        ids = [e["id"] for e in result["elements"]]
        storey = model.by_type("IfcBuildingStorey")[0]
        assert storey.id() in ids

    def test_storey_elements_includes_contained(self, model):
        storey = model.by_type("IfcBuildingStorey")[0]
        result = relations(model, storey)
        ids = [e["id"] for e in result["elements"]]
        wall = model.by_type("IfcWall")[0]
        assert wall.id() in ids

    def test_elements_no_duplicates(self, model):
        storey = model.by_type("IfcBuildingStorey")[0]
        result = relations(model, storey)
        ids = [e["id"] for e in result["elements"]]
        assert len(ids) == len(set(ids))

    def test_elements_all_have_id_and_type(self, model):
        wall = model.by_type("IfcWall")[0]
        result = relations(model, wall)
        for e in result["elements"]:
            assert "id" in e
            assert "type" in e

    def test_traverse_up_has_no_elements_field(self, model):
        wall = model.by_type("IfcWall")[0]
        result = relations(model, wall, traverse="up")
        assert isinstance(result, list)
        assert not any("elements" in item for item in result)


class TestJsonSerializable:
    def test_relations_serializable(self, model):
        wall = model.by_type("IfcWall")[0]
        result = relations(model, wall)
        json.dumps(result)

    def test_traverse_serializable(self, model):
        wall = model.by_type("IfcWall")[0]
        result = relations(model, wall, traverse="up")
        json.dumps(result)


class TestCLI:
    @staticmethod
    def _ifc_path(model):
        f = tempfile.NamedTemporaryFile(suffix=".ifc", delete=False)
        model.write(f.name)
        f.close()
        return f.name

    def test_relations_json(self, model):
        path = self._ifc_path(model)
        try:
            wall = model.by_type("IfcWall")[0]
            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", path, "relations", str(wall.id())],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert data["type"] == "IfcWall"
            assert "hierarchy" in data
        finally:
            os.unlink(path)

    def test_relations_traverse_up(self, model):
        path = self._ifc_path(model)
        try:
            wall = model.by_type("IfcWall")[0]
            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", path, "relations", str(wall.id()), "--traverse", "up"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert isinstance(data, list)
            assert data[0]["type"] == "IfcWall"
            assert data[-1]["type"] == "IfcProject"
        finally:
            os.unlink(path)

    def test_relations_bad_id(self, model):
        path = self._ifc_path(model)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", path, "relations", "999999"],
                capture_output=True,
                text=True,
            )
            assert result.returncode != 0
            assert "Error" in result.stderr
        finally:
            os.unlink(path)


def _by_name(model, ifc_class, name):
    return next(e for e in model.by_type(ifc_class) if e.Name == name)


def _refs(entities):
    return [{"id": e.id(), "type": e.is_a(), **({"name": e.Name} if e.Name else {})} for e in entities]


class TestStructuralRelations:
    def test_no_structural_block_without_structural_links(self, model):
        assert "structural" not in relations(model, model.by_type("IfcWall")[0])

    def test_member(self, structural_model):
        f = structural_model
        member = _by_name(f, "IfcStructuralCurveMember", "Cantilever")
        structural = relations(f, member)["structural"]
        assert structural == {
            "analysis_models": _refs(f.by_type("IfcStructuralAnalysisModel")),
            "connections": _refs(
                [
                    _by_name(f, "IfcStructuralPointConnection", "Root"),
                    _by_name(f, "IfcStructuralPointConnection", "Tip"),
                ]
            ),
            "building_elements": _refs(f.by_type("IfcBeam")),
        }

    def test_connection(self, structural_model):
        f = structural_model
        tip = _by_name(f, "IfcStructuralPointConnection", "Tip")
        structural = relations(f, tip)["structural"]
        assert structural["members"] == _refs(f.by_type("IfcStructuralCurveMember"))
        assert structural["activities"] == _refs(f.by_type("IfcStructuralPointAction"))

    def test_building_element(self, structural_model):
        f = structural_model
        structural = relations(f, f.by_type("IfcBeam")[0])["structural"]
        assert structural == {"structural_members": _refs(f.by_type("IfcStructuralCurveMember"))}

    def test_activity(self, structural_model):
        f = structural_model
        structural = relations(f, f.by_type("IfcStructuralPointAction")[0])["structural"]
        assert structural == {
            "item": _refs([_by_name(f, "IfcStructuralPointConnection", "Tip")])[0],
            "load_groups": _refs([_by_name(f, "IfcStructuralLoadGroup", "Point loads")]),
        }

    def test_load_case(self, structural_model):
        f = structural_model
        case = _by_name(f, "IfcStructuralLoadCase", "Live")
        structural = relations(f, case)["structural"]
        combination = _by_name(f, "IfcStructuralLoadGroup", "ULS")
        assert structural == {"load_combinations": [{**_refs([combination])[0], "factor": 3.0}]}

    def test_load_combination(self, structural_model):
        f = structural_model
        combination = _by_name(f, "IfcStructuralLoadGroup", "ULS")
        structural = relations(f, combination)["structural"]
        case = _by_name(f, "IfcStructuralLoadCase", "Live")
        assert structural == {
            "analysis_models": _refs(f.by_type("IfcStructuralAnalysisModel")),
            "load_cases": [{**_refs([case])[0], "factor": 3.0}],
        }

    def test_structural_entities_are_in_the_flat_list(self, structural_model):
        f = structural_model
        result = relations(f, _by_name(f, "IfcStructuralPointConnection", "Tip"))
        ids = {e["id"] for e in result["elements"]}
        assert f.by_type("IfcStructuralCurveMember")[0].id() in ids
        assert f.by_type("IfcStructuralPointAction")[0].id() in ids
