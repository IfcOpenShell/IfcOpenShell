import bpy
import os
import shutil

# import tool
import bonsai.tool as tool


def refresh():
    IfcGitData.is_loaded = False


class IfcGitData:

    data = {}
    is_loaded = False

    @classmethod
    def make_sure_is_loaded(cls):
        if not cls.is_loaded:
            cls.load()

    @classmethod
    def load(cls):
        cls.data = {
            "repo": cls.repo(),
            "remotes": cls.remotes(),
            "branch_names": cls.branch_names(),
            "remote_names": cls.remote_names(),
            "remote_urls": cls.remote_urls(),
            "path_ifc": cls.path_ifc(),
            "branches_by_hexsha": cls.branches_by_hexsha(),
            "tags_by_hexsha": cls.tags_by_hexsha(),
            "name_ifc": cls.name_ifc(),
            "dir_name": cls.dir_name(),
            "base_name": cls.base_name(),
            "working_dir": cls.working_dir(),
            "untracked_files": cls.untracked_files(),
            "is_detached": cls.is_detached(),
            "active_branch_name": cls.active_branch_name(),
            "is_dirty": cls.is_dirty(),
            "commit": cls.commit(),
            "current_revision": cls.current_revision(),
            "git_exe": cls.git_exe(),
            "ifcmerge_exe": cls.ifcmerge_exe(),
        }
        cls.is_loaded = True

    @classmethod
    def repo(cls):
        if bool(tool.Ifc.get()):
            path_ifc = tool.Ifc.get_path()
            if os.path.isfile(path_ifc):
                return tool.IfcGit.repo_from_path(path_ifc)
        return None

    @classmethod
    def remotes(cls):
        if cls.repo():
            return cls.repo().remotes
        return None

    @classmethod
    def branch_names(cls):
        return []

    @classmethod
    def remote_names(cls):
        return []

    @classmethod
    def remote_urls(cls):
        result = {}
        if cls.repo():
            for remote in cls.repo().remotes:
                result[remote.name] = remote.url
        return result

    @classmethod
    def path_ifc(cls):
        path_ifc = tool.Ifc.get_path()
        if os.path.isfile(path_ifc):
            return tool.Ifc.get_path()
        return None

    @classmethod
    def branches_by_hexsha(cls):
        try:
            if tool.IfcGitRepo.repo.branches:
                return tool.IfcGit.branches_by_hexsha(tool.IfcGitRepo.repo)
        except AttributeError:
            return {}

    @classmethod
    def tags_by_hexsha(cls):
        if tool.IfcGitRepo.repo:
            return tool.IfcGit.tags_by_hexsha(tool.IfcGitRepo.repo)
        return {}

    @classmethod
    def name_ifc(cls):
        if bool(tool.Ifc.get()):
            path_ifc = tool.Ifc.get_path()
            if tool.IfcGitRepo.repo and os.path.isfile(path_ifc):
                working_dir = tool.IfcGitRepo.repo.working_dir
                return os.path.relpath(path_ifc, working_dir)
        return None

    @classmethod
    def dir_name(cls):
        if bool(tool.Ifc.get()):
            path_ifc = tool.Ifc.get_path()
            if os.path.isfile(path_ifc):
                return os.path.dirname(path_ifc)
        return None

    @classmethod
    def base_name(cls):
        if bool(tool.Ifc.get()):
            path_ifc = tool.Ifc.get_path()
            if os.path.isfile(path_ifc):
                return os.path.basename(path_ifc)
        return None

    @classmethod
    def working_dir(cls):
        if cls.repo():
            return cls.repo().working_dir

    @classmethod
    def untracked_files(cls):
        if cls.repo():
            return cls.repo().untracked_files
        return []

    @classmethod
    def is_detached(cls):
        if cls.repo():
            return cls.repo().head.is_detached

    @classmethod
    def active_branch_name(cls):
        if cls.repo() and not cls.is_detached():
            return cls.repo().active_branch.name

    @classmethod
    def is_dirty(cls):
        if cls.repo() and cls.git_exe():
            path_ifc = tool.Ifc.get_path()
            if os.path.isfile(path_ifc):
                return cls.repo().is_dirty(path=path_ifc)
        return False

    @classmethod
    def commit(cls):
        props = bpy.context.scene.IfcGitProperties
        if cls.repo() and len(props.ifcgit_commits) > 0:
            item = props.ifcgit_commits[props.commit_index]
            try:
                return cls.repo().commit(rev=item.hexsha)
            except ValueError:
                return

    @classmethod
    def current_revision(cls):
        props = bpy.context.scene.IfcGitProperties
        if cls.repo() and cls.repo().head.is_valid() and len(props.ifcgit_commits) > 0:
            return tool.IfcGitRepo.repo.commit()

    @classmethod
    def git_exe(cls):
        return shutil.which("git")

    @classmethod
    def ifcmerge_exe(cls):
        return shutil.which("ifcmerge")
