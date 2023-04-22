import bpy
from bpy.types import PropertyGroup

from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
    IntProperty,
    EnumProperty,
)

from data import IfcGitData


def git_branches(self, context):
    """branches enum"""

    # NOTE "Python must keep a reference to the strings returned by
    # the callback or Blender will misbehave or even crash"
    IfcGitData.data["branch_names"] = sorted(
        [branch.name for branch in IfcGitData.data["repo"].heads]
    )

    if "main" in IfcGitData.data["branch_names"]:
        IfcGitData.data["branch_names"].remove("main")
        IfcGitData.data["branch_names"] = ["main"] + IfcGitData.data["branch_names"]

    return [(myname, myname, myname) for myname in IfcGitData.data["branch_names"]]


def update_revlist(self, context):
    """wrapper to trigger update of the revision list"""

    bpy.ops.ifcgit.refresh()
    props = context.scene.IfcGitProperties
    props.commit_index = 0


class IfcGitListItem(PropertyGroup):
    """Group of properties representing an item in the list."""

    hexsha: StringProperty(
        name="Git hash",
        description="checksum for this commit",
        default="Uncommitted data!",
    )
    relevant: BoolProperty(
        name="Is relevant",
        description="does this commit reference our ifc file",
        default=False,
    )


class IfcGitProperties(PropertyGroup):

    ifcgit_commits: CollectionProperty(type=IfcGitListItem, name="List of git items")
    commit_index: IntProperty(name="Index for my_list", default=0)
    commit_message: StringProperty(
        name="Commit message",
        description="A human readable description of these changes",
        default="",
    )
    new_branch_name: StringProperty(
        name="New branch name",
        description="A short name used to refer to this branch",
        default="",
    )
    display_branch: EnumProperty(items=git_branches, update=update_revlist)
    ifcgit_filter: EnumProperty(
        items=[
            ("all", "All", "All revisions"),
            ("tagged", "Tagged", "Tagged revisions"),
            ("relevant", "Relevant", "Revisions for this project"),
        ],
        update=update_revlist,
    )
