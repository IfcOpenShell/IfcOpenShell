from behave.model import Scenario


def before_all(context):
    userdata = context.config.userdata
    context.localedir = userdata["localedir"]

    continue_after_failed = True
    Scenario.continue_after_failed_step = continue_after_failed
