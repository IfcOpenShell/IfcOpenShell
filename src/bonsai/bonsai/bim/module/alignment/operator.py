# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>, 2022 Yassine Oualid <yassine@sigmadimensions.com>
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

# pyright: reportUnnecessaryTypeIgnoreComment=error

import os

import ifcopenshell.api.alignment
import ifcopenshell.api.alignment.add_stationing_to_alignment

import bpy
import json
import time
import calendar
import isodate
import bonsai.core.sequence as core
import bonsai.tool as tool
import bonsai.bim.module.sequence.helper as helper
import ifcopenshell.api.spatial
import ifcopenshell.geom
import ifcopenshell.util.sequence
import ifcopenshell.util.selector
from datetime import datetime
from dateutil import parser, relativedelta
from bpy_extras.io_utils import ImportHelper
from typing import get_args, TYPE_CHECKING
from typing_extensions import assert_never


class ImportAlignmentCSV(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_alignment_csv"
    bl_label = "Import Alignment CSV"
    bl_description = " Import alignment from the provided .csv file."
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        elif ifc_file.schema != "IFC4X3":
            cls.poll_message_set("Schema must be IFC4x3.")
            return False
        return True

    def _execute(self, context):
        self.file = tool.Ifc.get()
        start = time.time()
        alignment = ifcopenshell.api.alignment.create_alignment_from_csv(self.file, self.filepath)
        ifcopenshell.api.alignment.create_geometric_representation(self.file, alignment)
        ifcopenshell.api.alignment.add_stationing_to_alignment(self.file, alignment=alignment, start_station=0.0)

        # IFC 4.1.5.1 alignments cannot be contained in spatial structures, but can be referenced into them
        sites = self.file.by_type("IfcSite")
        for site in sites:
            ifcopenshell.api.spatial.reference_structure(self.file, products=[alignment], relating_structure=site)

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

        self.report({"INFO"}, "Imported in %s seconds" % (time.time() - start))
