# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2022 Martina Jakubowska <martina@jakubowska.dk>
#
# This file is part of IfcSverchok.
#
# IfcSverchok is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcSverchok is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IfcSverchok.  If not, see <http://www.gnu.org/licenses/>.

from os.path import abspath, splitext
import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.aggregate
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.util.element
import ifcsverchok.helper
import ifcsverchok.helper as helper
from ifcsverchok.ifcstore import SvIfcStore
from bpy.props import StringProperty, BoolProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, flatten_data


class SvIfcWriteFile(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    """
    Triggers: Ifc write to file
    Tooltip: Write transient Ifc file to path
    """

    def refresh_node_local(self, context):
        if self.refresh_local:
            self.process()
            self.refresh_local = False

    refresh_local: BoolProperty(
        name="Write", description="Write to file when changed to True.", update=refresh_node_local
    )

    bl_idname = "SvIfcWriteFile"
    bl_label = "IFC Write File"
    path: StringProperty(
        name="path",
        description="File path to write to. Can be relative.",
        update=updateNode,
    )

    def sv_init(self, context):
        helper.create_socket(
            self.inputs,
            "path",
            description="File path to write to. Can be relative.",
            data_type="str",
            prop_name="path",
        )
        helper.create_socket(
            self.outputs,
            "output",
            description="Node result output message.",
            data_type="str",
            prop_name="output",
        )

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        tooltip = (
            "Writes active Ifc file to path.\n "
            "It will overwrite an existing file.\n"
            "N.B.! It's recommended to create a fresh IFC File using the 're-run all nodes' button in IfcSverchok panel before saving."
        )
        row.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = tooltip
        row.prop(self, "refresh_local", icon="FILE_REFRESH")

    def process(self):
        path = flatten_data(self.inputs["path"].sv_get(), target_level=1)[0]
        if not path:
            return
        path = abspath(path)
        file = SvIfcStore.get_file()
        _, ext = splitext(path)
        if not ext:
            raise Exception("Bad path. Provide a path to a file.")
        if self.refresh_local and ext:
            self.ensure_hirarchy(file)
            file.write(path)
        self.outputs["output"].sv_set(f"File written successfully to: {path}.")

    def ensure_hirarchy(self, file: ifcopenshell.file) -> None:
        # TODO: same code as ifc.write_file_panel?
        elements_in_buildings = []
        if not 0 <= 0 < len(file.by_type("IfcBuilding")):
            my_building = ifcopenshell.api.root.create_entity(file, ifc_class="IfcBuilding", name="My Building")
            elements = ifcopenshell.util.element.get_decomposition(my_building)
        else:
            for building in file.by_type("IfcBuilding"):
                elements = ifcopenshell.util.element.get_decomposition(building)
                elements_in_buildings.extend(elements)

        for spatial in file.by_type("IfcSpatialElement") or file.by_type("IfcSpatialStructureElement"):
            if not (spatial.is_a("IfcSite") or spatial.is_a("IfcBuilding")) and (spatial not in elements_in_buildings):
                elements = ifcopenshell.util.element.get_decomposition(spatial)
                ifcopenshell.api.aggregate.assign_object(
                    file,
                    products=[spatial],
                    relating_object=file.by_type("IfcBuilding")[0],
                )

        elements_in_buildings_after = []
        for building in file.by_type("IfcBuilding"):
            elements = ifcopenshell.util.element.get_decomposition(building)
            elements_in_buildings_after.extend(elements)

        elements = file.by_type("IfcElement")
        for element in elements:
            if element not in elements_in_buildings:
                ifcopenshell.api.spatial.assign_container(
                    file,
                    products=[element],
                    relating_structure=file.by_type("IfcBuilding")[0],
                )

        for building in file.by_type("IfcBuilding"):
            elements = ifcopenshell.util.element.get_decomposition(building)
            if not building.Decomposes:
                if not 0 <= 0 < len(file.by_type("IfcSite")):
                    ifcopenshell.api.root.create_entity(file, ifc_class="IfcSite", name="My Site")
                ifcopenshell.api.aggregate.assign_object(
                    file,
                    products=[building],
                    relating_object=file.by_type("IfcSite")[0],
                )
                try:
                    if file.by_type("IfcSite")[0].Decomposes[0].RelatingObject.is_a("IfcProject"):
                        continue
                except IndexError:
                    pass
                ifcopenshell.api.aggregate.assign_object(
                    file,
                    products=[file.by_type("IfcSite")[0]],
                    relating_object=file.by_type("IfcProject")[0],
                )
        self.file = file
        return


def register():
    bpy.utils.register_class(SvIfcWriteFile)


def unregister():
    bpy.utils.unregister_class(SvIfcWriteFile)
