import os

from behave.model import Scenario
from logfile import create_logfile
from logfile import append_logfile
from zoom_smart_view import append_zoom_smartview
from zoom_smart_view import create_zoom_smartview
from bimtester.ifc import IfcStore
from bimtester.lang import switch_locale


this_path = os.path.dirname(os.path.realpath(__file__))


def before_all(context):
    userdata = context.config.userdata

    if context.config.lang:
        switch_locale(userdata.get("localedir"), context.config.lang)

    context.ifc_path = userdata["ifc"]
    context.ifc_basename = os.path.basename(
        os.path.splitext(context.ifc_path)[0]
    )

    continue_after_failed = userdata.getbool(
        "runner.continue_after_failed_step", True
    )
    Scenario.continue_after_failed_step = continue_after_failed

    # keep out path
    context.outpath = os.path.join(this_path, "..")

    # since bimtesterfc directory in tmp is removed on every run
    # neither log file nor sm file does need to be explicit removed first

    # set up log file
    context.thelogfile = os.path.join(
        context.outpath,
        context.ifc_basename + ".log"
    )
    create_logfile(
        context.thelogfile,
        context.ifc_basename,
    )

    # set up smart view file
    context.smview_file = os.path.join(
        context.outpath,
        context.ifc_basename + ".bcsv"
    )
    create_zoom_smartview(
        context.smview_file,
        context.ifc_basename,
    )


def after_step(context, step):

    if step.status == "failed":

        # append log file
        append_logfile(context, step)

        # extend smart view
        if hasattr(context, "falseguids"):
            # print(context.falseguids)

            append_zoom_smartview(
                context.smview_file,
                step.name,
                context.falseguids
            )
