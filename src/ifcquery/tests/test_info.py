from ifcquery.info import info


class TestInfo:
    def test_basic_attributes(self, model):
        wall = model.by_type("IfcWall")[0]
        result = info(model, wall)
        assert result["id"] == wall.id()
        assert result["type"] == "IfcWall"
        assert result["attributes"]["Name"] == "Wall001"

    def test_container(self, model):
        wall = model.by_type("IfcWall")[0]
        result = info(model, wall)
        assert result["container"]["type"] == "IfcBuildingStorey"
        assert result["container"]["name"] == "Ground Floor"

    def test_project_info(self, model):
        project = model.by_type("IfcProject")[0]
        result = info(model, project)
        assert result["type"] == "IfcProject"
        assert result["attributes"]["Name"] == "TestProject"

    def test_all_attributes_serializable(self, model):
        """All attribute values should be JSON-serializable (no entity instances)."""
        import json

        wall = model.by_type("IfcWall")[0]
        result = info(model, wall)
        # Should not raise
        json.dumps(result)
