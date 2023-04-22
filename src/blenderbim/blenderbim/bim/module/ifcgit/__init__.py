#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# 2023 Bruno Postle <bruno@postle.net>, Bruno Perdigão <brunoperdigao@tutanota.com>,
# Massimo Fabbro <maxfb87@yahoo.it>

# import os
# import sys
import bpy
from . import ui, prop, operator

# sys.path.insert(0, "/home/bruno/src/ifc-git")
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# bl_info = {
#         "name": "IFC Git",
#         "author": "Bruno Postle",
#         "location": "Scene > IFC Git",
#         "description": "Manage IFC files in Git repositories",
#         "blender": (2, 80, 0),
#         "category": "Import-Export",
#     }

classes = (
        operators.AddFileToRepo,
        operators.CommitChanges,
        operators.CreateRepo,
        operators.DiscardUncommitted,
        operators.DisplayRevision,
        operators.DisplayUncommitted,
        operators.Merge,
        operators.RefreshGit,
        operators.SwitchRevision,
        prop.IfcGitListItem,
        prop.IfcGitProperties,
        ui.IFCGIT_PT_panel,
        ui.COMMIT_UL_List,
    )




def register():
        bpy.types.Scene.IfcGitProperties = bpy.props.PointerProperty(type=prop.IfcGitProperties)


def unregister():
    del bpy.types.Scene.IfcGitProperties
