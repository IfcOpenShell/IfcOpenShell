#!/usr/bin/env python3

import argparse

from bimtester import clean
from bimtester import reports
from bimtester import run


def show_widget(features="", ifcfile=""):

    import sys
    from PySide2 import QtWidgets

    from bimtester.guiwidget import GuiWidgetBimTester

    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)

    # Create and show the form
    form = GuiWidgetBimTester(features, ifcfile)
    form.show()

    # Run the main Qt loop
    sys.exit(app.exec_())


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Runs unit tests for BIM data"
    )
    parser.add_argument(
        "-p",
        "--purge",
        action="store_true",
        help="Purge tests of deleted elements"
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
        "-c",
        "--console",
        action="store_true",
        help="Show results in the console"
    )
    parser.add_argument(
        "-f",
        "--feature",
        type=str,
        help="Specify a feature file to test",
        default=""
    )
    parser.add_argument(
        "-a",
        "--advanced-arguments",
        type=str,
        help="Specify your own arguments to Python's Behave",
        default=""
    )
    parser.add_argument(
        "-g",
        "--gui",
        action="store_true",
        help=(
            "Start the gui. The option t (run in temp directory) "
            "is triggered automaticly."
        )
    )
    parser.add_argument(
        "featuresdir",
        type=str,
        nargs="?",
        help=(
            "Specify a features directory. This should contain "
            " a directory named features which contains all the "
            "feature files."
        ),
        default=""
    )
    parser.add_argument(
        "ifcfile",
        type=str,
        nargs="?",
        help=(
            "Specify a ifc file."
        ),
        default=""
    )

    args = vars(parser.parse_args())
    print(args)

    if args["purge"]:
        clean.TestPurger().purge()
    elif args["report"]:
        reports.generate_report()
    elif args["gui"]:
        show_widget(args["featuresdir"], args["ifcfile"])
    else:
        run.run_tests(args)
        if args["report_after_run"]:
            reports.generate_report()
    print("# All tasks are complete :-)")
