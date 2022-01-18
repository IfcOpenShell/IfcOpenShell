import test.bootstrap
import ifcopenshell.api


class TestCreateFile(test.bootstrap.IFC4):
    def test_run(self):
        ifc = ifcopenshell.api.run("project.create_file")
        assert ifc.schema == "IFC4"
        ifc = ifcopenshell.api.run("project.create_file", version="IFC2X3")
        assert ifc.schema == "IFC2X3"
        assert ifc.wrapped_data.header.file_name.name == "/dev/null"
        assert ifc.wrapped_data.header.file_name.time_stamp
        assert "IfcOpenShell" in ifc.wrapped_data.header.file_name.preprocessor_version
        assert "IfcOpenShell" in ifc.wrapped_data.header.file_name.originating_system
        assert ifc.wrapped_data.header.file_name.authorization == "Nobody"
        assert ifc.wrapped_data.header.file_description.description == ("ViewDefinition[DesignTransferView]",)
