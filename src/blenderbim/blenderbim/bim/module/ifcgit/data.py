import bpy
import os
import shutil
import tool
import blenderbim.tool as btool


def refresh():
    IfcGitData.is_loaded = False


class IfcGitData:

    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "repo": cls.repo(),
            "branch_names": cls.branch_names(),
            "path_ifc": cls.path_ifc(),
            "branches_by_hexsha": cls.branches_by_hexsha(),
            "tags_by_hexsha": cls.tags_by_hexsha(),
            "name_ifc": cls.name_ifc(),
            "dir_name": cls.dir_name(),
            "base_name": cls.base_name(),
            "is_dirty": cls.is_dirty(),
            "commit": cls.commit(),
            "current_revision": cls.current_revision(),
            "git_exe": cls.git_exe(),
            "ifcmerge_exe": cls.ifcmerge_exe(),
        }
        cls.is_loaded = True

    @classmethod
    def repo(cls):
        if bool(btool.Ifc.get()):
            path_ifc = btool.Ifc.get_path()
            if not os.path.isfile(path_ifc):
                return None
            return tool.IfcGit.repo_from_path(path_ifc)
        else:
            return tool.IfcGitRepo.repo

    @classmethod
    def branch_names(cls):
        return []

    @classmethod
    def path_ifc(cls):
        return btool.Ifc.get_path()

    @classmethod
    def branches_by_hexsha(cls):
        try:
            if tool.IfcGitRepo.repo.branches:
                return tool.IfcGit.branches_by_hexsha(tool.IfcGitRepo.repo)
        except:
            return {}

    @classmethod
    def tags_by_hexsha(cls):
        if tool.IfcGitRepo.repo:
            return tool.IfcGit.tags_by_hexsha(tool.IfcGitRepo.repo)
        return {}

    @classmethod
    def name_ifc(cls):
        if bool(btool.Ifc.get()):
            path_ifc = btool.Ifc.get_path()
        if tool.IfcGitRepo.repo:
            working_dir = tool.IfcGitRepo.repo.working_dir
            return os.path.relpath(path_ifc, working_dir)
        return None

    @classmethod
    def dir_name(cls):
        if bool(btool.Ifc.get()):
            path_ifc = btool.Ifc.get_path()
            if not os.path.isfile(path_ifc):
                return None
            return os.path.dirname(path_ifc)
        return None

    @classmethod
    def base_name(cls):
        if bool(btool.Ifc.get()):
            path_ifc = btool.Ifc.get_path()
            return os.path.basename(path_ifc)
        return None

    @classmethod
    def is_dirty(cls):
        if tool.IfcGitRepo.repo and cls.git_exe():
            path_ifc = btool.Ifc.get_path()
            return tool.IfcGitRepo.repo.is_dirty(path=path_ifc)
        return False

    @classmethod
    def commit(cls):
        props = bpy.context.scene.IfcGitProperties
        if len(props.ifcgit_commits) > 0:
            item = props.ifcgit_commits[props.commit_index]
            return tool.IfcGitRepo.repo.commit(rev=item.hexsha)

    @classmethod
    def current_revision(cls):
        props = bpy.context.scene.IfcGitProperties
        if len(props.ifcgit_commits) > 0:
            return tool.IfcGitRepo.repo.commit()

    @classmethod
    def git_exe(cls):
        return shutil.which("git")

    @classmethod
    def ifcmerge_exe(cls):
        return shutil.which("ifcmerge")
