def create_repo(ifcgit, ifc):
    path_ifc = ifc.get_path()
    path_dir = ifcgit.get_path_dir(path_ifc)
    ifcgit.init_repo(path_dir)


def add_file(ifcgit, ifc):
    path_ifc = ifc.get_path()
    repo = ifcgit.repo_from_path(path_ifc)
    ifcgit.add_file_to_repo(repo, path_ifc)


def clone_repo(ifcgit, remote_url, local_folder, operator):
    repo = ifcgit.clone_repo(remote_url, local_folder)
    if not repo:
        operator.report({"ERROR"}, "Clone failed")
        return
    operator.report({"INFO"}, "Repository cloned")
    ifcgit.load_anyifc(repo)


def discard_uncommitted(ifcgit, ifc):
    path_ifc = ifc.get_path()
    # NOTE this is calling the git binary in a subprocess
    ifcgit.git_checkout(path_ifc)
    ifcgit.load_project(path_ifc)


def commit_changes(ifcgit, ifc, repo):
    """Commit and create new branches as required"""
    path_ifc = ifc.get_path()

    if repo.head.is_detached:
        ifcgit.git_commit(path_ifc)
        ifcgit.create_new_branch()
    else:
        ifcgit.checkout_new_branch(path_ifc)
        ifcgit.git_commit(path_ifc)


def add_tag(ifcgit, repo):
    ifcgit.add_tag(repo)


def delete_tag(ifcgit, repo, tag_name):
    ifcgit.delete_tag(repo, tag_name)


def add_remote(ifcgit, repo):
    ifcgit.add_remote(repo)


def delete_remote(ifcgit, repo):
    ifcgit.delete_remote(repo)


def push(ifcgit, repo, remote_name, operator):
    error_message = ifcgit.push(repo, remote_name, repo.active_branch.name)
    if error_message:
        operator.report({"ERROR"}, error_message)


def refresh_revision_list(ifcgit, repo, ifc):
    if repo.heads:
        ifcgit.refresh_revision_list(ifc.get_path())


def colourise_revision(ifcgit):

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
    ifcgit.refresh_revision_list(path_ifc)


def merge_branch(ifcgit, ifc, operator):
    path_ifc = ifc.get_path()
    ifcgit.config_ifcmerge()
    ifcgit.execute_merge(path_ifc, operator)


def entity_log(ifcgit, ifc, step_id, operator):
    path_ifc = ifc.get_path()
    log_text = ifcgit.entity_log(path_ifc, step_id)
    # ERROR is only way to display a multi-line message
    operator.report({"ERROR"}, log_text)
