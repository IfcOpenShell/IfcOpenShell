import os
from behave.model import Scenario

from bimtester.ifc import IfcStore
from bimtester.lang import switch_locale
from logfile import append_logfile
from logfile import create_logfile
from zoom_smart_view import add_smartview
from zoom_smart_view import create_zoom_set_of_smartviews


this_path = os.path.dirname(os.path.realpath(__file__))


def before_all(context):

    userdata = context.config.userdata
    context.locale_dir = userdata.get("localedir")

    if context.config.lang:
        switch_locale(context.locale_dir, context.config.lang)

    continue_after_failed = userdata.getbool("runner.continue_after_failed_step", True)
    Scenario.continue_after_failed_step = continue_after_failed

    # context.ifc_path = userdata.get("ifc", "")
    context.ifcfile_basename = os.path.basename(
        os.path.splitext(userdata["ifc"])[0]
    )
    context.outpath = os.path.join(this_path, "..")
    context.create_log = False
    context.create_smartview = False

    if context.create_log is True:
        # set up log file
        context.thelogfile = os.path.join(
            context.outpath,
            context.ifcfile_basename + ".log"
        )
        create_logfile(
            context.thelogfile,
            context.ifcfile_basename,
        )


def before_feature(context, feature):

    # https://github.com/IfcOpenShell/IfcOpenShell/issues/1910#issuecomment-989732600
    # messages language, parsed by behaves lang argument
    print("Messages language: {}".format(context.config.lang))
    # features file language, set in feature files first line
    # html report will use this too
    print("Features language: {}".format(context.feature.language))

    # if messages lang is not set use features lang
    if context.config.lang == "" or context.config.lang is None:
        context.config.lang = context.feature.language
        print("Switch messages language to: {}".format(context.config.lang))
        switch_locale(context.locale_dir, context.config.lang)

    # TODO: refactor zoom smart view support into a decoupled module
    if context.create_smartview is True:
        smartview_name = context.ifcfile_basename + "_" + feature.name
        context.smview_file = os.path.join(
            context.outpath,
            smartview_name + ".bcsv"
        )
        # print("SmartView file: {}".format(context.smview_file))
        create_zoom_set_of_smartviews(
            context.smview_file,
            smartview_name,
        )


def after_step(context, step):

    if step.status == "failed" and context.create_log is True:
        append_logfile(context, step)

    if (
        step.status == "failed"
        and context.create_smartview is True
        and hasattr(context, "falseguids")
    ):
        # print(context.falseguids)
        add_smartview(
            context.smview_file,
            step.name,
            context.falseguids
        )
