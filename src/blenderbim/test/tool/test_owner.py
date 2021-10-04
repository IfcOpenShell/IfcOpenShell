import bpy
import ifcopenshell
import test.bim.bootstrap
import blenderbim.core.tool
import blenderbim.tool as tool
from blenderbim.tool.owner import Owner as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Owner)


class TestSetUser(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        user = ifc.createIfcPersonAndOrganization()
        subject.set_user(user)
        assert bpy.context.scene.BIMOwnerProperties.active_user_id == user.id()


class TestGetUser(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert subject.get_user() is None
        TestSetUser().test_run()
        user = tool.Ifc.get().by_type("IfcPersonAndOrganization")[0]
        assert subject.get_user() == user


class TestClearUser(test.bim.bootstrap.NewFile):
    def test_run(self):
        TestSetUser().test_run()
        subject.clear_user()
        assert bpy.context.scene.BIMOwnerProperties.active_user_id == 0
