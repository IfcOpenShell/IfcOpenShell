# IfcPatch - IFC patching utiliy
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.


class Patcher:
    def __init__(self, src, file, logger):
        """Allow ArchiCAD IFC spaces to open as Revit rooms

        The underlying problem is that Revit does not bring in IFC spaces as
        spaces / rooms in Revit when you link an IFC in Revit. This has been
        broken for at least 3 years and counting. This is a problem typically
        for ArchiCAD architects who want to send rooms to MEP folks using
        Revit.

        See bug: https://github.com/Autodesk/revit-ifc/issues/15

        The solution is to open an IFC in Revit instead of linking it, which
        will convert IFC spaces into Revit rooms. However, there are very
        specific scenarios where Revit will convert these rooms, which have
        been painstakingly reverse engineered through trial and error.
        Firstly, the rooms should have a lower bound with a Z value matching
        the Z value of the storey it is on. Secondly, although faceted breps
        do work in some scenarios (I assume Revit has an internal topological
        analysis tool), conversion to an extruded area solid yield much more
        robust results. Finally, changing the Precision value to an obscene
        number very strangely seems to cause a lot more rooms to be converted
        successfully.

        This patch is designed to only work on ArchiCAD IFC exports where the
        only contents of the IFC is IFC space and `nothing else`. It also
        requires you to run it using Blender, as the geometric modification
        uses the Blender geometry engine.

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "FixArchiCADToRevitSpaces", "arguments": []})
        """
        self.src = src
        self.file = file
        self.logger = logger

    def patch(self):
        import bpy
        import bonsai.tool as tool
        import ifcopenshell
        import ifcopenshell.util.element
        from bonsai.bim.ifc import IfcStore
        from mathutils import Vector, Matrix

        if len(bpy.data.objects) > 0:
            bpy.data.batch_remove(bpy.data.objects)
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

        bpy.ops.bim.load_project(filepath=self.src)

        def recalculate_origin(wall):
            new_origin = wall.matrix_world @ Vector(wall.bound_box[0])
            if (wall.matrix_world.translation - new_origin).length < 0.001:
                return
            wall.data.transform(
                Matrix.Translation(
                    (wall.matrix_world.inverted().to_quaternion() @ (wall.matrix_world.translation - new_origin))
                )
            )
            wall.matrix_world.translation = new_origin

        for obj in bpy.context.visible_objects:
            bpy.context.view_layer.update()
            if "IfcSpace" not in obj.name:
                continue

            element = tool.Ifc.get_entity(obj)
            storey = ifcopenshell.util.element.get_aggregate(element)
            storey_obj = tool.Ifc.get_object(storey)
            target_z = storey_obj.location.z

            local_target_z = (obj.matrix_world.inverted() @ Vector((0, 0, target_z))).z
            local_target_zup = (obj.matrix_world.inverted() @ Vector((0, 0, target_z + 3))).z
            for v in obj.data.vertices:
                if round(v.co.z, 3) == 0:
                    v.co.z = local_target_z
            bpy.context.view_layer.update()
            recalculate_origin(obj)
            obj.select_set(True)

        bpy.ops.bim.update_representation(
            ifc_representation_class="IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids"
        )
        for context in IfcStore.get_file().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.Precision:
                context.Precision = 10

        self.file = IfcStore.get_file()
