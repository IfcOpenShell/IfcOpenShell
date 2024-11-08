# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy.props
import bpy.types


class AuginProperties(bpy.types.PropertyGroup):
    username: bpy.props.StringProperty(name="Username")
    password: bpy.props.StringProperty(name="Password")
    token: bpy.props.StringProperty(name="Token")
    project_name: bpy.props.StringProperty(name="Project Name")
    project_filename: bpy.props.StringProperty(name="IFC Filename")
    is_success: bpy.props.BoolProperty(name="Is Successful Upload", default=False)
