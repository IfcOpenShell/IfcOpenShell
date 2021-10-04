import blenderbim.core.geometry as subject
from test.core.bootstrap import ifc, surveyor

class TestEditObjectPlacement:
    def test_run(self, ifc, surveyor):
        ifc.get_entity("obj").should_be_called().will_return("element")
        surveyor.get_absolute_matrix("obj").should_be_called().will_return("matrix")
        ifc.run("geometry.edit_object_placement", product="element", matrix="matrix").should_be_called()
        subject.edit_object_placement(ifc, surveyor, obj="obj")
