#!/usr/bin/env python3

import argparse
import os

from bimtester import clean
from bimtester import reports
from bimtester import run


def show_widget(features="", ifcfile="", get_featurepath_from_ifcpath=False):

    import sys
    from PySide2 import QtWidgets

    from bimtester.guiwidget import GuiWidgetBimTester

    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)

    # Create and show the form
    form = GuiWidgetBimTester(features, ifcfile, get_featurepath_from_ifcpath)
    form.show()

    # Run the main Qt loop
    sys.exit(app.exec_())


if __name__ == "__main__":

    # TODO make similar to bash commands
    # use - not _ in named args

    parser = argparse.ArgumentParser(
        description="Runs unit tests for BIM data"
    )
    parser.add_argument(
        "-a",
        "--advanced-arguments",
        type=str,
        help="Specify your own arguments to Python's Behave",
        default=""
    )
    parser.add_argument(
        "-c",
        "--console",
        action="store_true",
        help="Show results in the console"
    )
    parser.add_argument(
        "-d",
        "--featuresdir",
        type=str,
        help=(
            "Specify a features directory. This should contain "
            "a directory named 'features' which contains all the "
            "feature files."
        ),
        default=""
    )
    parser.add_argument(
        "-g",
        "--gui",
        action="store_true",
        help=(
            "Start the gui. The option t (copyintemprun) "
            "is triggered automaticly."
        )
    )
    parser.add_argument(
        "-f",
        "--feature",
        type=str,
        help="Specify a feature file to test",
        default=""
    )
    parser.add_argument(
        "-i",
        "--ifcfile",
        type=str,
        help=(
            "Specify a ifc file."
        ),
        default=""
    )
    parser.add_argument(
        "-p",
        "--purge",
        action="store_true",
        help="Purge tests of deleted elements"
    )
    parser.add_argument(
        "-path",
        "--path",
        type=str,
        help=(
            "Specify a path to prepend to feature and ifc file"
        ),
        default=""
    )
    parser.add_argument(
        "-r",
        "--report",
        action="store_true",
        help="Generate a HTML report"
    )
    parser.add_argument(
        "-rr",
        "--report_after_run",
        action="store_true",
        help="Generate a HTML report after running the tests"
    )
    parser.add_argument(
        "-t",
        "--copyintemprun",
        action="store_true",
        help=(
            "Copy steps and feature files into a temporary directory "
            "and run bimtester with them."
        )
    )

    args = vars(parser.parse_args())
    from json import dumps
    print(dumps(args, indent=4))

    if args["path"]:
        if args["feature"]:
            args["feature"] = os.path.join(args["path"], args["feature"])
        if not args["gui"]:
            args["ifcfile"] = os.path.join(args["path"], args["ifcfile"])

    if args["purge"]:
        clean.TestPurger().purge()
    elif args["report"]:
        reports.generate_report()
    elif args["gui"]:
        fea = args["featuresdir"]
        ifc = args["ifcfile"]
        if fea != "" and ifc != "":
            show_widget(fea, ifc, False)
        elif fea == "" and ifc != "":
            show_widget(fea, ifc, True)
    elif args["copyintemprun"]:
        run.run_copyintmp_tests(args)
    else:
        run.run_tests(args)
        if args["report_after_run"]:
            reports.generate_report()

    print("# All tasks are complete :-)")
