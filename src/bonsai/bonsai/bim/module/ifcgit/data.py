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
        repo = None
        if bool(tool.Ifc.get()):
            path_ifc = tool.Ifc.get_path()
            if os.path.isfile(path_ifc):
                repo = tool.IfcGit.repo_from_path(path_ifc)

        cls.data = {
            "repo": repo,
            "remotes": repo.remotes if repo else None,
            "branch_names": cls.branch_names(repo),
            "tag_names": cls.tag_names(repo),
            "remote_names": cls.remote_names(repo),
            "remote_urls": {r.name: r.url for r in repo.remotes} if repo else {},
            "path_ifc": cls.path_ifc(),
            "branches_by_hexsha": cls.branches_by_hexsha(),
            "tags_by_hexsha": cls.tags_by_hexsha(),
            "name_ifc": cls.name_ifc(repo),
            "dir_name": cls.dir_name(),
            "base_name": cls.base_name(),
            "working_dir": repo.working_dir if repo else None,
            "ifc_is_untracked": cls.ifc_is_untracked(repo),
            "is_detached": repo.head.is_detached if repo else None,
            "active_branch_name": repo.active_branch.name if repo and not repo.head.is_detached else None,
            "is_dirty": cls.is_dirty(repo),
            "current_revision": cls.current_revision(repo),
            "git_exe": cls.git_exe(),
            "ifcmerge_exe": cls.ifcmerge_exe(),
        }
        cls.is_loaded = True

    @classmethod
    def branch_names(cls, repo):
        if not repo or not repo.heads:
            return []
        names = sorted([b.name for b in repo.branches])
        if "main" in names:
            names.remove("main")
            names = ["main"] + names
        if repo.remotes:
            for remote in repo.remotes:
                for ref in remote.refs:
                    names.append(ref.name)
        return names

    @classmethod
    def tag_names(cls, repo):
        if not repo:
            return []
        return [t.name for t in repo.tags]

    @classmethod
    def remote_names(cls, repo):
        if not repo:
            return []
        names = sorted([r.name for r in repo.remotes])
        if "origin" in names:
            names.remove("origin")
            names = ["origin"] + names
        return names

    @classmethod
    def path_ifc(cls):
        path_ifc = tool.Ifc.get_path()
        if os.path.isfile(path_ifc):
            return path_ifc
        return None

    @classmethod
    def branches_by_hexsha(cls):
        try:
            if tool.IfcGitRepo.repo.branches:
                return tool.IfcGit.branches_by_hexsha(tool.IfcGitRepo.repo)
        except AttributeError:
            pass
        return {}

    @classmethod
    def tags_by_hexsha(cls):
        if tool.IfcGitRepo.repo:
            return tool.IfcGit.tags_by_hexsha(tool.IfcGitRepo.repo)
        return {}

    @classmethod
    def name_ifc(cls, repo):
        if bool(tool.Ifc.get()) and repo:
            path_ifc = tool.Ifc.get_path()
            if os.path.isfile(path_ifc):
                return os.path.relpath(path_ifc, repo.working_dir)
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
    def ifc_is_untracked(cls, repo):
        """Return True if the IFC file exists in the repo but has not been added to git."""
        if not repo:
            return False
        path_ifc = tool.Ifc.get_path()
        if not os.path.isfile(path_ifc):
            return False
        return not bool(repo.git.ls_files(path_ifc))

    @classmethod
    def is_dirty(cls, repo):
        if repo and cls.git_exe():
            path_ifc = tool.Ifc.get_path()
            if os.path.isfile(path_ifc):
                return repo.is_dirty(path=path_ifc)
        return False

    @classmethod
    def current_revision(cls, repo):
        props = tool.IfcGit.get_ifcgit_props()
        if repo and repo.head.is_valid() and len(props.ifcgit_commits) > 0:
            return repo.commit()

    @classmethod
    def git_exe(cls):
        return shutil.which("git")

    @classmethod
    def ifcmerge_exe(cls):
        return shutil.which("ifcmerge")
