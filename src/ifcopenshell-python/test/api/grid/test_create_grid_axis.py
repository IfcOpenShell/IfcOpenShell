import test.bootstrap
import ifcopenshell.api


class TestCreateGridAxis(test.bootstrap.IFC4):
    def test_run(self):
        grid = self.file.createIfcGrid()
        axis = ifcopenshell.api.run(
            "grid.create_grid_axis", self.file, axis_tag="axis_tag", same_sense=True, uvw_axes="UAxes", grid=grid
        )
        assert axis.AxisTag == "axis_tag"
        assert axis.SameSense is True
        assert grid.UAxes == (axis,)
        axis2 = ifcopenshell.api.run(
            "grid.create_grid_axis", self.file, axis_tag="axis_tag", same_sense=True, uvw_axes="UAxes", grid=grid
        )
        assert grid.UAxes == (axis, axis2)
