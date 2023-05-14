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

import bpy
from . import ui, prop, operator


classes = (
    operator.AddFileToRepo,
    operator.AddTag,
    operator.CloneRepo,
    operator.CommitChanges,
    operator.CreateRepo,
    operator.DiscardUncommitted,
    operator.DisplayRevision,
    operator.DisplayUncommitted,
    operator.Merge,
    operator.RefreshGit,
    operator.SwitchRevision,
    prop.IfcGitTag,
    prop.IfcGitListItem,
    prop.IfcGitProperties,
    ui.IFCGIT_PT_panel,
    ui.COMMIT_UL_List,
)


def register():
    bpy.types.Scene.IfcGitProperties = bpy.props.PointerProperty(type=prop.IfcGitProperties)


def unregister():
    del bpy.types.Scene.IfcGitProperties
