from behave.model import Scenario


def before_all(context):
    userdata = context.config.userdata
    continue_after_failed = userdata.getbool("runner.continue_after_failed_step", True)
    Scenario.continue_after_failed_step = continue_after_failed
