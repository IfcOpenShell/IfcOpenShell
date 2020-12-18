from behave.model import Scenario


def before_all(context):
    userdata = context.config.userdata
    context.localedir = userdata.get("localedir")
    continue_after_failed = userdata.getbool("runner.continue_after_failed_step", True)
    Scenario.continue_after_failed_step = continue_after_failed
