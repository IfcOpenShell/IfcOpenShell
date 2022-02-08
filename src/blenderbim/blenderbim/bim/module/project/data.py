# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import os
import bpy
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore


def refresh():
    ProjectData.is_loaded = False


class ProjectData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "export_schema": cls.get_export_schema(),
            "template_file": cls.template_file(),
            "last_saved": cls.last_saved(),
        }
        cls.is_loaded = True

    @classmethod
    def get_export_schema(cls):
        return [(s, s, "") for s in IfcStore.schema_identifiers]

    @classmethod
    def template_file(cls):
        files = os.listdir(os.path.join(bpy.context.scene.BIMProperties.data_dir, "libraries"))
        results = [("0", "Blank Project", "")]
        results.extend([(f, f.replace(".ifc", ""), "") for f in files if ".ifc" in f])
        return results

    @classmethod
    def last_saved(cls):
        ifc = tool.Ifc.get()
        if not ifc:
            return ""
        try:
            save_datetime = ifc.wrapped_data.header.file_name.time_stamp
            save_date, save_time = save_datetime.split("T")
            return f"{save_date} {':'.join(save_time.split(':')[0:2])}"
        except:
            return ""
