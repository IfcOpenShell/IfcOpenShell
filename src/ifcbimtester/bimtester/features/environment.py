from behave.model import Scenario


def before_all(context):
    userdata = context.config.userdata
    context.ifcbasename = userdata["ifcbasename"]
    context.localedir = userdata.get("localedir")

    # do not break after a failed scenario
    # https://community.osarch.org/discussion/comment/3328/#Comment_3328
    continue_after_failed = userdata.getbool("runner.continue_after_failed_step", True)
    Scenario.continue_after_failed_step = continue_after_failed
