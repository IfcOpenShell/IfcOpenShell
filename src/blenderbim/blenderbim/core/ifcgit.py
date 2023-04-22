def create_repo(ifcgit, ifc):
    path_ifc = ifc.get_path()
    path_dir = ifcgit.get_path_dir(path_ifc)
    ifcgit.init_repo(path_dir)


def add_file(ifcgit, ifc):
    path_ifc = ifc.get_path()
    repo = ifcgit.repo_from_path(path_ifc)
    ifcgit.add_file_to_repo(repo, path_ifc)


def discard_uncomitted(ifcgit, ifc):
    path_ifc = ifc.get_path()
    # NOTE this is calling the git binary in a subprocess
    ifcgit.git_checkout(path_ifc)
    ifcgit.load_project(path_ifc)


def commit_changes(ifcgit, ifc, repo, context):
    path_ifc = ifc.get_path()
    ifcgit.git_commit(path_ifc)

    if repo.head.is_detached:
        ifcgit.create_new_branch()


def refresh_revision_list(ifcgit, repo, ifc):
    ifcgit.clear_commits_list()
    path_ifc = ifc.get_path()
    lookup = ifcgit.tags_by_hexsha(repo)
    ifcgit.get_commits_list(path_ifc, lookup)


def colourise_revision(ifcgit, context):

    step_ids = ifcgit.get_revisions_step_ids()
    if not step_ids:
        return
    modified_shape_object_step_ids = ifcgit.get_modified_shape_object_step_ids(step_ids)
    final_step_ids = ifcgit.update_step_ids(step_ids, modified_shape_object_step_ids)
    ifcgit.colourise(final_step_ids)


def colourise_uncommitted(ifcgit, ifc, repo):
    path_ifc = ifc.get_path()
    step_ids = ifcgit.ifc_diff_ids(repo, None, "HEAD", path_ifc)
    ifcgit.colourise(step_ids)


def switch_revision(ifcgit, ifc):
    # FIXME bad things happen when switching to a revision that predates current project

    path_ifc = ifc.get_path()
    ifcgit.switch_to_revision_item()
    ifcgit.load_project(path_ifc)


def merge_branch(ifcgit, ifc, operator):
    path_ifc = ifc.get_path()
    ifcgit.config_ifcmerge()
    ifcgit.execute_merge(path_ifc, operator)
