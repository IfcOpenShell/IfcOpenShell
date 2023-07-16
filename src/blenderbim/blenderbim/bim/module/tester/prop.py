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

from blenderbim.bim.prop import StrProperty
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)

def purge():
    pass

def get_failure_entities():
    return



class Specification(PropertyGroup):
    name: StringProperty(name="Name")
    status : BoolProperty(default=False, name="Status")

class FailedEntities(PropertyGroup):
    reason: StringProperty(name="Reason")
    element: StringProperty(name="Element")
    

class IfcTesterProperties(PropertyGroup):
    specs: StringProperty(default="", name="IDS File")    
    ifc_file: StringProperty(default="", name="IFC File")
    should_load_from_memory: BoolProperty(default=False, name="Load from Memory")
    
    active_specification_index: IntProperty(name="Active Specification Index")   
    active_requirement_index: IntProperty(name="Active Requirement Index")
    active_failed_entity_index: IntProperty(name="Active Failed Entity Index")  
    report: StringProperty(default="", name="JSON report")
    specifications: CollectionProperty(name="Specifications", type=Specification)
    failed_entities: CollectionProperty(name="FailedEntities", type=FailedEntities)
    has_report : BoolProperty(default=False, name="")
    has_entities : BoolProperty(default=False, name="")


    
