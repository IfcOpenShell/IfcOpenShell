import behave.formatter.pretty  # Needed for pyinstaller to package it
import os
import shutil
import sys
import tempfile
import webbrowser


# TODO: if the ifc file name or path contains special character
# like German Umlaute behave gives an error


# get bimtester source code module path
bimtester_path = os.path.dirname(os.path.realpath(__file__))
# print(bimtester_path)
locale_path = os.path.join(bimtester_path, "locale")


try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
except Exception:
    base_path = os.path.dirname(os.path.realpath(__file__))


def get_resource_path(relative_path):
    return os.path.join(base_path, relative_path)


def run_tests(args):

    print("# Run tests.")

    report_file = os.path.join("report", "report.json")

    if "copyintemprun" in args and args["copyintemprun"] is True:
        print("copyintemprun")
        is_copyintemprun = True
        args, copy_base_path = copy_intmp_tests(args)
        features_path = os.path.join(copy_base_path, "features")
        report_file = os.path.join(copy_base_path, report_file)

    else:
        print("No copyintemprun")
        is_copyintemprun = False
        if not get_features(args):
            print("No features could be found to check.")
            return False
        features_path = get_resource_path("features")

    # get behave args
    behave_args = get_behave_args(args, features_path, report_file)

    # run tests
    if behave_args != []:
        run_behave(behave_args)
    else:
        print("Error, not able to run behave because of empty behave args.")
        return False

    if is_copyintemprun is True:
        return report_file
    else:
        return True


def get_behave_args(args, features_path, report_file):

    if os.path.isdir(features_path):
        behave_args = [features_path]
    else:
        return []

    if os.path.isdir(locale_path):
        behave_args.extend([
            # path for translation files
            # next two lines are one arg
            "--define",
            "localedir={}".format(locale_path)
        ])
    else:
        print(
            "Error, translation locals path '{}' does not exist."
            .format(locale_path)
        )

    if args["advanced_arguments"]:
        behave_args.extend(args["advanced_arguments"].split())

    if args["ifcfile"]:
        behave_args.extend([
            # next two lines are one arg
            "--define",
            "ifcfile={}".format(args["ifcfile"])
        ])

    if args["path"]:
        behave_args.extend([
            # next two lines are one arg
            "--define",
            "path={}".format(args["path"])
        ])

    if not args["console"]:
        behave_args.extend([
            # redirect prints in step methods
            # if step fails some output is catched, thus might not be printed
            # https://github.com/behave/behave/issues/346
            "--no-capture",
            # next two lines are one arg
            "--format",
            "json.pretty",
            # report file, if relative, than relative to current shell path
            # next two lines are one arg
            "--outfile",
            report_file,
        ])

    return behave_args


def run_behave(behave_args):

    from json import dumps
    print(dumps(behave_args, indent=4))

    from behave.__main__ import main as behave_main
    behave_main(behave_args)
    print("# All tests are finished.")

    return True


def get_features(args):
    # current_path = os.path.abspath(".")
    features_dir = get_resource_path("features")
    for f in os.listdir(features_dir):
        if f.endswith(".feature"):
            os.remove(os.path.join(features_dir, f))
    if args["feature"]:
        shutil.copyfile(
            args["feature"],
            os.path.join(
                get_resource_path("features"),
                os.path.basename(args["feature"])
            )
        )
        return True
    if os.path.exists("features"):
        shutil.copytree("features", get_resource_path("features"))
        return True
    has_features = False
    for f in os.listdir("."):
        if not f.endswith(".feature"):
            continue
        if args["feature"] and args["feature"] != f:
            continue
        has_features = True
        shutil.copyfile(
            f,
            os.path.join(get_resource_path("features"), os.path.basename(f))
        )
    return has_features


"""
# clean logs to be able to run tests
# once again but on another building model and in another directory
# somehow does not work, thus test will be run in the same directory
# on each new run, directory will be deleted before each new run
# https://github.com/behave/behave/issues/871
# run bimtester
# copy manually this code, run bimtester again,
# does not work on two directories
from behave.runner_util import reset_runtime
reset_runtime()

"""


def copy_intmp_tests(args={}):

    print("# Copy features and steps to temp.")

    from behave import __version__ as behave_version
    # https://github.com/behave/behave/issues/871
    if behave_version == "1.2.5":
        print(
            "At least behave version 1.2.6 is needed, but version {} found."
            .format(behave_version)
        )
        return False

    # print(args)
    # get the features_path, the dir where the feature files to test are in
    if ("featuresdir" in args and args["featuresdir"] != ""):
        is_features = True
        the_features_path = os.path.join(args["featuresdir"], "features")
        if not os.path.isdir(the_features_path):
            print(
                "Error, the features directory '{}' does not exist."
                .format(the_features_path)
            )
            return False
    else:
        is_features = False

    # get ifc path and ifc filename
    if ("ifcfile" in args and args["ifcfile"] != ""):
        is_ifcfile = True
        ifcfile = args["ifcfile"]
        if os.path.isfile(ifcfile) is not True:
            print("Error, the ifc file '{}' does not exist.".format(ifcfile))
            return False
        ifc_path = os.path.dirname(os.path.realpath(ifcfile))
        if os.path.isdir(ifc_path) is False:
            print("ifc path does not exist.")
            return False
    else:
        is_ifcfile = False

    # print(is_features)
    # print(is_ifcfile)

    if is_features is True and is_ifcfile is True:
        print("features given, ifcfile given.")

    elif is_features is False and is_ifcfile is True:
        print("features given, ifcfile NOT given.")
        # features = ifcfile directory
        the_features_path = os.path.join(ifc_path, "features")

    elif is_features is True and is_ifcfile is False:
        print("features given, ifcfile NOT given.")
        # the ifcfile provided in the feature files is used
        # TODO What will be passed as ifcfile arg?
        print("Not yet implemented.")
        return False

    elif is_features is False and is_ifcfile is False:
        print("features NOT given, ifcfile NOT given.")
        # the current directory = features
        # the ifcfile provided in the feature files is used
        # TODO What will be passed as ifcfile arg?
        print("Not yet implemented.")
        return False

    else:
        print("Error: this should never happen, please debug.")
        return False

    # set up paths
    # a unique temp path should not be used
    # behave raises an ambiguous step exception
    # copy_base_path = tempfile.mkdtemp()
    # thus use the same path on every run
    # but delete it if exists
    copy_base_path = os.path.join(tempfile.gettempdir(), "bimtesterfc")
    if os.path.isdir(copy_base_path):
        from shutil import rmtree
        rmtree(copy_base_path)  # fails on read only files
    if os.path.isdir(copy_base_path):
        print(
            "Delete former beimtester run dir '{}' failed"
            .format(copy_base_path)
        )
        return False
    os.mkdir(copy_base_path)
    copy_features_path = os.path.join(copy_base_path, "features")

    # copy features path from bimtester source code
    srccode_features_path = os.path.join(
        bimtester_path,
        "features",
    )
    # print(srccode_features_path)
    if os.path.exists(srccode_features_path):
        shutil.copytree(srccode_features_path, copy_features_path)
    else:
        print(
            "Bimtester source code features directory {} not found."
            .format(srccode_features_path)
        )
        return False

    # copy features files
    # print(the_features_path)
    # print(copy_features_path)
    # parameter dirs_exist_ok=True, from py 3.8
    # if os.path.exists(the_features_path):
    #     shutil.copytree(
    #         the_features_path,
    #         copy_features_path,
    #         dirs_exist_ok=True
    # )

    # copy feature files
    feature_files = os.listdir(the_features_path)
    # print(feature_files)
    for feature_file in feature_files:
        cp_feature_file = os.path.join(copy_features_path, feature_file)
        # print(feature_file)
        # copy file
        shutil.copyfile(
            os.path.join(the_features_path, feature_file),
            cp_feature_file
        )

    return args, copy_base_path


def run_all(args):

    print("# Run all.")

    # run bimtester
    report_file = run_tests(args)
    print(report_file)

    # check if it worked out well
    if report_file is False:
        print("BIMTester behave tests returned False.")
        return False

    if not os.path.isfile(report_file):
        print("Report directory does not exist. This should not happen. Debug")
        return False

    # create html report and open in webbrowser
    from .reports import generate_report
    generate_report(report_file=report_file)
    # get the feature files
    feature_files = os.listdir(
        os.path.join(args["featuresdir"], "features")
    )
    # print(feature_files)
    for ff in feature_files:
        webbrowser.open(os.path.join(
            os.path.dirname(report_file),
            ff + ".html"
        ))

    return True
