# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

# ############################################################################ #

# Hey there! Welcome to the Bonsai code. Please feel free to reach
# out if you have any questions or need further guidance. Happy hacking!

# ############################################################################ #

# Every module has a tool file which implements all the functions that the core
# needs. Whereas the core is simply high level code, the tool file has the
# concrete implementations, dealing with exactly how things interact with
# Blender's property systems, IFC's data structures, the filesystem, geometry
# processing, and more.

import ifcopenshell.settings
import bpy
import bonsai.core.tool
import bonsai.tool as tool
import ifcopenshell.api
import ifcopenshell.api.alignment
import ifcopenshell
import ifcopenshell.api.cogo

# There is always one class in each tool file, which implements the interface
# defined by `core/tool.py`.
class Alignment(bonsai.core.tool.Alignment):
    @classmethod
    def add_survey_point(cls,x,y):
        model = tool.Ifc.get()
        point = model.createIfcCartesianPoint((x,y))
        annotation = ifcopenshell.api.cogo.add_survey_point(model,point)

        m = tool.Loader.create_point_cloud_mesh(annotation.Representation.Representations[0])
        tool.Ifc.link(annotation.Representation.Representations[0],m)

        # create a new Blender object
        annotation_obj = bpy.data.objects.new(tool.Loader.get_name(annotation), m)

        # link the blender object to with the IFC element
        tool.Geometry.link(annotation, annotation_obj)

        # assign the object to the blender collections
        tool.Collector.assign(annotation_obj, should_clean_users_collection=False)


    @classmethod
    def build(cls):
        coordinates = [(0.0,0.0),(100.0,0.0),(1000.,200.)]
        radii = [(100.)]

        vpoints = [(0.0,0.0),(100.0,0.0),(200.0,150.0)]
        lengths = [(50.)]

        model = tool.Ifc.get()
   
        # create an IfcAlignment with Name="Dummy"
        alignment = ifcopenshell.api.alignment.create_alignment_by_pi_method(model,"Dummy",coordinates,radii,vpoints,lengths)

        ifcopenshell.api.alignment.create_geometric_representation(model, alignment)
        ifcopenshell.api.alignment.add_stationing_to_alignment(model, alignment=alignment, start_station=0.0)

        # IFC 4.1.5.1 alignments cannot be contained in spatial structures, but can be referenced into them
        sites = model.by_type("IfcSite")
        for site in sites:
            ifcopenshell.api.spatial.reference_structure(model, products=[alignment], relating_structure=site)

        # process the generated IfcReferent for the alignment
        for rel in alignment.IsNestedBy:
            for referent in rel.RelatedObjects:
                if referent.is_a("IfcReferent"):
                    referent_obj = bpy.data.objects.new(tool.Loader.get_name(referent), None)
                    tool.Geometry.link(referent, referent_obj)
                    tool.Collector.assign(referent_obj, should_clean_users_collection=False)

        # an alignment can be an aggregation of multiple child alignments (ie. multiple verticals for a single horizontal)
        # get all the alignment curves
        curves = []
        for rel in alignment.IsDecomposedBy:
            for agg in rel.RelatedObjects:
                if agg.is_a("IfcAlignment"):
                    curves.append(ifcopenshell.api.alignment.get_curve(agg))  # 3D curve

        # if there aren't any curves from aggregation, then there is only a single vertical or no vertical
        if len(curves) == 0:
            curves.append(ifcopenshell.api.alignment.get_curve(alignment))

        settings = ifcopenshell.geom.settings()
        for curve in curves:
            shape = ifcopenshell.geom.create_shape(settings, curve)

            # create a new Blender mesh
            mesh_name = tool.Loader.get_mesh_name_from_shape(shape)
            mesh = bpy.data.meshes.new(mesh_name)
            m = tool.Loader.convert_geometry_to_mesh(shape, mesh)

            # create a new Blender object
            alignment_obj = bpy.data.objects.new(tool.Loader.get_name(alignment), m)

            # link the blender object to with the alignment element
            tool.Geometry.link(alignment, alignment_obj)

            # assign the object to the blender collections
            tool.Collector.assign(alignment_obj, should_clean_users_collection=False)
