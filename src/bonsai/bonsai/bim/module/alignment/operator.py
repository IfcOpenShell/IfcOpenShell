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

# ############################################################################ #

# Hey there! Welcome to the Bonsai code. Please feel free to reach
# out if you have any questions or need further guidance. Happy hacking!

# ############################################################################ #

# Every module has an operator.py file to define all of the buttons that a user
# can click on from the Blender interface. Blender calls these buttons
# "Operators", since they correlate to a single user operation.

import os

import ifcopenshell.api.alignment
import ifcopenshell.api.alignment.add_stationing_to_alignment

import bpy
import json
import time
import calendar
import isodate
import bonsai.core.alignment as core
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



# Each button correlates to a class like the one below. In this case, we're
# creating a new button that will execute a hello world feature.
class BuildAlignment(bpy.types.Operator, tool.Ifc.Operator):
    # Every operator has a unique ID. If you enable Python tooltips and hover
    # over any button in the interface, you will see each button will run a
    # function that uses this ID. For example, hovering over this button will
    # show that the code it executes is "bpy.ops.bim.demonstrate_hello_world()"
    bl_idname = "bim.build_alignment"

    # In the interface, this button will have the text "Build Alignment".
    bl_label = "Build Alignment"

    # This code means that the user can undo or redo after pressing the button.
    bl_options = {"REGISTER", "UNDO"}

    # When hovering over the button, this helpful description will be shown.
    bl_description = "Builds a dummy alignment"

    # When the button is pressed, this _execute() function will run.
    def _execute(self, context):
        # Every operator should do one thing only: execute a core function. In
        # order to execute a core function, the operator's responsibility is to
        # pass in all of the inputs the core needs to do its job.

        # A core function simply tells tools what to do, so a core function will
        # always need at least one tool as an input.
        core.build_alignment(tool.Alignment)

class SurveyPoint(bpy.types.Operator,tool.Ifc.Operator):
    bl_idname = "bim.add_survey_point"
    bl_label = "Add Survey Point"
    bl_options = {"REGISTER","UNDO"}
    bl_description = "Adds a survey point"
    def _execute(self,context):
        core.add_survey_point(tool.Alignment,x=bpy.context.scene.BIMAlignmentBuilderProperties.x,y=bpy.context.scene.BIMAlignmentBuilderProperties.y)