# Saikei Civil - Civil Engineering Tools for IfcOpenShell
# Copyright (C) 2025 IfcOpenShell Contributors
#
# This file is part of Saikei Civil.
#
# Saikei Civil is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Saikei Civil is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Saikei Civil.  If not, see <http://www.gnu.org/licenses/>.

"""
Civil module - Core civil engineering functionality

This module follows Bonsai's architecture pattern with dynamic module loading.
"""

import bpy
import importlib
from . import handler, ui, prop, operator

# Feature modules - add new modules here
modules = {
    "alignment": None,
    # Future modules:
    # "vertical": None,
    # "corridor": None,
    # "cross_section": None,
}

# Dynamically import all modules using relative import path
# Use __name__ to get the correct package path regardless of how Blender loads us
for name in modules.keys():
    modules[name] = importlib.import_module(f".module.{name}", package=__name__)

# Collect all classes from global and module files
classes = [
    prop.SaikeiCivilProperties,
]

# Add classes from each feature module
for mod in modules.values():
    classes.extend(mod.classes)


def register():
    """Register all classes and properties"""
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register global properties
    bpy.types.Scene.SaikeiCivilProperties = bpy.props.PointerProperty(type=prop.SaikeiCivilProperties)

    # Register each module
    for mod in modules.values():
        mod.register()


def unregister():
    """Unregister all classes and properties in reverse order"""
    # Unregister modules first
    for mod in reversed(list(modules.values())):
        mod.unregister()

    # Remove global properties
    del bpy.types.Scene.SaikeiCivilProperties

    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
