# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>, @Andrej730
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bmesh

import ifcopenshell
import bonsai.tool as tool

import json
import zipfile
import os.path


def update_sverchok_modifier(context):
    obj = context.active_object
    props = obj.BIMSverchokProperties
    element = tool.Ifc.get_entity(obj)
    psets = ifcopenshell.util.element.get_psets(element)
    pset = psets.get("BBIM_Sverchok", None)
    sverchok_data = json.loads(pset["Data"]) if pset else dict()

    vertices = sverchok_data.get("vertices", [])
    edges = sverchok_data.get("edges", [])
    faces = sverchok_data.get("polygons", [])

    bm = bmesh.new()
    bm.verts.index_update()
    bm.edges.index_update()
    bm.faces.index_update()

    new_verts = [bm.verts.new(v) for v in vertices]
    new_edges = [bm.edges.new([new_verts[vi] for vi in edge]) for edge in edges]
    new_faces = [bm.faces.new([new_verts[vi] for vi in face]) for face in faces]
    bm.verts.index_update()
    bm.edges.index_update()
    bm.faces.index_update()

    if context.active_object.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()
    tool.Ifc.edit(obj)


# UI operators
class CreateNewSverchokGraph(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.create_new_sverchok_graph"
    bl_label = "Create New Sverchok Graph"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        import sverchok

        obj = context.active_object
        props = obj.BIMSverchokProperties

        node_group = bpy.data.node_groups.new("IfcNodeTree", type="SverchCustomTreeType")
        plane = node_group.nodes.new(type="SvPlaneNodeMk3")
        plane.sizex = 1
        plane.sizey = 1
        sverchok.ui.sv_temporal_viewers.add_temporal_viewer_draw(
            node_group.nodes, node_group.links, plane, cut_links=True
        )
        viewer = [n for n in node_group.nodes if n.bl_idname == "SvViewerDrawMk4"][0]
        viewer.label = f"IFCOutput {viewer.label}"

        props.node_group = node_group
        return {"FINISHED"}


class DeleteSverchokGraph(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.delete_sverchok_graph"
    bl_label = "Delete Selected Sverchok Graph"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMSverchokProperties
        bpy.data.node_groups.remove(props.node_group)
        return {"FINISHED"}

    def draw(self, context):
        self.layout.label(text="WARNING. The graph will be removed permanently.")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class UpdateDataFromSverchok(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.update_data_from_sverchok"
    bl_label = "Update Data From Sverchok"
    bl_options = {"REGISTER"}

    def invoke(self, context, event):
        if not context.active_object.BIMSverchokProperties.node_group:
            return context.window_manager.invoke_props_dialog(self)
        return self._execute(context)

    def draw(self, context):
        self.layout.label(text="WARNING. Sverchok data will be emptied")
        self.layout.label(text="because no sverchok node group is selected.")

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMSverchokProperties
        node_group = props.node_group

        if node_group:
            output_node = [
                n
                for n in node_group.nodes
                if n.bl_idname == "SvViewerDrawMk4" and n.label.lower().startswith("ifcoutput")
            ]

            if not output_node:
                error_msg = (
                    f"Couldn't find output node in node group {node_group.name}.\n"
                    'Output node should be type of "Viewer Draw" and it\'s label should start with "ifcoutput".'
                )
                self.report({"ERROR"}, (error_msg))
                return {"CANCELLED"}

            output_node = output_node[0]

            sverchok_data = {
                "vertices": output_node.inputs["Vertices"].sv_get(deepcopy=False, default=[]),
                "edges": output_node.inputs["Edges"].sv_get(deepcopy=False, default=[]),
                "polygons": output_node.inputs["Polygons"].sv_get(deepcopy=False, default=[]),
            }

            # sv_get returns array of 1 element arrays, for convenience we reduce it to just 1 level array
            def try_first_element(x):
                return x[0] if x else x

            for key in sverchok_data:
                sverchok_data[key] = try_first_element(sverchok_data[key])
        else:
            sverchok_data = {"vertices": [], "edges": [], "polygons": []}

        print("sverchok data to upload: ", sverchok_data)
        psets = ifcopenshell.util.element.get_psets(element)
        pset = psets.get("BBIM_Sverchok", None)

        if pset:
            pset = tool.Ifc.get().by_id(pset["id"])
        else:
            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="BBIM_Sverchok")

        ifcopenshell.api.run(
            "pset.edit_pset",
            tool.Ifc.get(),
            pset=pset,
            properties={"Data": tool.Ifc.get().createIfcText(json.dumps(sverchok_data))},
        )
        update_sverchok_modifier(context)

        return {"FINISHED"}


# https://github.com/nortikin/sverchok/blob/a470f9d5c84090773d3f4a98ad04a8aca7492b33/ui/sv_IO_panel.py#L188-L237
# used code from Sverchok's SvNodeTreeImporter licensed under GPL v3
# the code was changed to work with ifc sverchok modifier
# removed the part that was relying on node graph to be opened at execution
class ImportSverchokGraph(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.import_sverchok_graph"
    bl_label = "Import Sverchok Graph"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty(
        name="File Path", description="Filepath used to import from", maxlen=1024, default="", subtype="FILE_PATH"
    )

    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})

    def _execute(self, context):
        import sverchok

        importer = sverchok.utils.sv_json_import.JSONImporter.init_from_path(self.filepath)
        obj = context.active_object
        props = obj.BIMSverchokProperties

        node_group = context.scene.io_panel_properties.import_tree
        if not node_group:
            node_group = props.node_group or bpy.data.node_groups.new("IfcNodeTree", type="SverchCustomTreeType")

        importer.import_into_tree(node_group)
        if importer.has_fails:
            self.report({"ERROR"}, importer.fail_massage)
        props.node_group = node_group
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        col = self.layout.column()
        col.label(text="Destination tree to import JSON:")
        col.template_ID(context.scene.io_panel_properties, "import_tree", new="node.new_import_tree")


# https://github.com/nortikin/sverchok/blob/a470f9d5c84090773d3f4a98ad04a8aca7492b33/ui/sv_IO_panel.py#L104-L185
# used code from Sverchok's SvNodeTreeExporter licensed under GPL v3
# the code was changed to work with ifc sverchok modifier
# removed the part that was relying on node graph to be opened at execution
class ExportSverchokGraph(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.export_sverchok_graph"
    bl_label = "Export Sverchok Graph"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty(
        name="File Path", description="Filepath used for exporting to", maxlen=1024, default="", subtype="FILE_PATH"
    )

    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})

    compact: bpy.props.BoolProperty(default=True, description="Compact representation of the JSON file")
    compress: bpy.props.BoolProperty()

    def _execute(self, context):
        import sverchok

        obj = context.active_object
        props = obj.BIMSverchokProperties
        ng = props.node_group
        destination_path = self.filepath
        if not destination_path.lower().endswith(".json"):
            destination_path += ".json"

        # future: should check if filepath is a folder or ends in \
        layout_dict = sverchok.utils.sv_json_export.JSONExporter.get_tree_structure(ng)

        if not layout_dict:
            msg = "no update list found - didn't export"
            self.report({"WARNING"}, msg)
            return {"CANCELLED"}

        indent = None if self.compact else 2
        with open(destination_path, "w") as fpo:
            json.dump(layout_dict, fpo, indent=indent)  # json_struct doesn't expect sort_keys = True
        msg = "exported to: " + destination_path
        self.report({"INFO"}, msg)

        if self.compress:
            comp_mode = zipfile.ZIP_DEFLATED

            # destination path = /a../b../c../somename.json
            base = os.path.basename(destination_path)  # somename.json
            basedir = os.path.dirname(destination_path)  # /a../b../c../

            # somename.zip
            final_archivename = base.replace(".json", "") + ".zip"

            # /a../b../c../somename.zip
            fullpath = os.path.join(basedir, final_archivename)

            with zipfile.ZipFile(fullpath, "w", compression=comp_mode) as myzip:
                myzip.write(destination_path, arcname=base)

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        graph_name = context.active_object.BIMSverchokProperties.node_group.name
        self.layout.label(text=f'Save node tree "{graph_name}" into json:')

        col = self.layout.column(heading="Options")  # new syntax in >= 2.90
        col.use_property_split = True
        col.prop(self, "compact")
        col.prop(self, "compress", text="Create ZIP archive")
