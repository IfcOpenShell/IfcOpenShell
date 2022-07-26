# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
from . import ui, prop, operator

classes = (
    operator.RefreshPsetTemplates,
    operator.AddPsetFile,
    operator.SavePsetTemplateFile,
    operator.AddPsetTemplate,
    operator.EditPsetTemplate,
    operator.RemovePsetTemplate,
    operator.AddPropTemplate,
    operator.EditPropTemplate,
    operator.RemovePropTemplate,
    operator.EnableEditingPsetTemplate,
    operator.DisableEditingPsetTemplate,
    operator.EnableEditingPropTemplate,
    operator.DeletePropEnum,
    operator.AddPropEnum,
    operator.DisableEditingPropTemplate,
    prop.PsetTemplate,
    prop.EnumerationValues,
    prop.PropTemplate,
    prop.BIMPsetTemplateProperties,
    ui.BIM_PT_pset_template,
)


def register():
    bpy.types.Scene.BIMPsetTemplateProperties = bpy.props.PointerProperty(type=prop.BIMPsetTemplateProperties)


def unregister():
    del bpy.types.Scene.BIMPsetTemplateProperties
