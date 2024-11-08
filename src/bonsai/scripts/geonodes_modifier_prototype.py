# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 @Andrej730
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


import ifcopenshell
import bonsai.tool as tool

import bpy
import bmesh
import json

# Below is the code for
# prototype for geonodes modifier (similar to ifc sverchok modifier)

# Since geonodes cannot be evaluated without input context (unlike sverchok)
# we add geonodes modifier to current object, add the node graph to it,
# get the data, save it to ifc pset and then remove the modifier.
# But it also saves the data taking into account all other existing modifiers.
# Removing other modifiers sounds a bit destructive
# but without it they will be reapplied to the saved geometry

# At this point I'm not sure if that's really will be useful for users and won't be just confusing.
# and therefore I leave this modifier just as prototype


def update_geometry_data():
    obj = bpy.context.active_object
    element = tool.Ifc.get_entity(obj)
    # props = obj.BIMGeonodesProperties
    # node_group = props.node_group
    node_group = bpy.data.node_groups["Geometry Nodes"]

    # get geo nodes modifier
    currently_added_modifiers = [m for m in obj.modifiers if m.type == "NODES" and m.node_group == node_group]
    if not currently_added_modifiers:
        m = obj.modifiers.new(name="ifc_geo_nodes", type="NODES")
        m.node_group = node_group
    else:
        m = currently_added_modifiers[0]
        m.node_group = node_group

    # save data to pset
    depsgraph = bpy.context.evaluated_depsgraph_get()
    geo_mesh = obj.evaluated_get(depsgraph).data
    geo_data = {
        "vertices": [v.co for v in geo_mesh.vertices],
        "edges": [e.vertices[:] for e in geo_mesh.edges],
        "polygons": [f.vertices[:] for f in geo_mesh.polygons],
    }
    psets = ifcopenshell.util.element.get_psets(element)
    pset = psets.get("BBIM_Geonodes", None)
    if pset:
        pset = tool.Ifc.get().by_id(pset["id"])
    else:
        pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="BBIM_Geonodes")
    ifcopenshell.api.run(
        "pset.edit_pset",
        tool.Ifc.get(),
        pset=pset,
        properties={"Data": json.dumps(geo_data, default=list)},
    )

    # remove the redundant modifier
    if not currently_added_modifiers:
        obj.modifiers.remove(m)

    # update current geometry from saved data
    update_geonodes_modifier()


def update_geonodes_modifier():
    obj = bpy.context.active_object
    element = tool.Ifc.get_entity(obj)
    psets = ifcopenshell.util.element.get_psets(element)
    pset = psets.get("BBIM_Geonodes", None)
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

    if bpy.context.active_object.mode == "EDIT":
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()
    obj.data.update()
    tool.Ifc.edit(obj)


if __name__ == "__main__":
    update_geometry_data()
