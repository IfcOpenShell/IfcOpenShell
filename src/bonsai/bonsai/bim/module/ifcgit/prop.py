from typing import TYPE_CHECKING, Literal

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

import bonsai.tool as tool
from bonsai.bim.module.ifcgit.data import IfcGitData


def git_branches(self: "IfcGitProperties", context: bpy.types.Context) -> tool.Blender.BLENDER_ENUM_ITEMS:
    # NOTE "Python must keep a reference to the strings returned by
    # the callback or Blender will misbehave or even crash"
    # Branch list (local + remote, main first) is computed once in IfcGitData.load()
    IfcGitData.make_sure_is_loaded()
    return [(name, name, name) for name in IfcGitData.data["branch_names"]]


def git_remotes(self: "IfcGitProperties", context: bpy.types.Context) -> tool.Blender.BLENDER_ENUM_ITEMS:
    IfcGitData.make_sure_is_loaded()
    return [(name, name, name) for name in IfcGitData.data["remote_names"]]


def update_revlist(self: "IfcGitProperties", context: bpy.types.Context) -> None:
    """wrapper to trigger update of the revision list"""

    bpy.ops.ifcgit.refresh()
    self.commit_index = 0


class IfcGitTag(PropertyGroup):
    """Properties of a Git tag"""

    name: StringProperty(
        name="Tag name",
        default="",
    )
    message: StringProperty(
        name="Tag message",
        default="",
    )

    if TYPE_CHECKING:
        name: str
        message: str


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
    author_name: StringProperty(
        name="Author Name",
        default="",
    )
    author_email: StringProperty(
        name="Author Email",
        default="",
    )
    message: StringProperty(
        name="Commit Message",
        default="",
    )
    committed_date: IntProperty(name="Committed Date", default=0)
    tags: CollectionProperty(type=IfcGitTag, name="List of revision tags")

    if TYPE_CHECKING:
        hexsha: str
        relevant: bool
        author_name: str
        author_email: str
        message: str
        committed_date: int
        tags: bpy.types.bpy_prop_collection_idprop[IfcGitTag]


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
    new_tag_name: StringProperty(
        name="New tag name",
        description="A short name used to refer to this tag",
        default="",
    )
    new_tag_message: StringProperty(
        name="Tag message (optional)",
        description="An optional human readable description of this tag",
        default="",
    )
    remote_name: StringProperty(
        name="New remote name",
        description="A local name for a remote Git repository",
        default="",
    )
    remote_url: StringProperty(
        name="Git URL",
        description="A URL pointing to a Git repository",
        default="",
    )
    local_folder: StringProperty(
        name="Local folder",
        description="A local Git repository path",
        default="",
        subtype="DIR_PATH",
    )
    display_branch: EnumProperty(items=git_branches, update=update_revlist)
    select_remote: EnumProperty(items=git_remotes)
    ifcgit_filter: EnumProperty(
        items=[
            ("all", "All", "All revisions"),
            ("tagged", "Tagged", "Tagged revisions"),
            ("relevant", "Relevant", "Revisions for this project"),
        ],
        update=update_revlist,
    )
    merge_conflicts: StringProperty(
        name="Merge Conflicts",
        description="JSON report from last failed merge attempt",
        default="",
    )

    if TYPE_CHECKING:
        ifcgit_commits: bpy.types.bpy_prop_collection_idprop[IfcGitListItem]
        commit_index: int
        commit_message: str
        new_branch_name: str
        new_tag_name: str
        new_tag_message: str
        remote_name: str
        remote_url: str
        local_folder: str
        display_branch: str
        select_remote: str
        ifcgit_filter: Literal["all", "tagged", "relevant"]
        merge_conflicts: str
