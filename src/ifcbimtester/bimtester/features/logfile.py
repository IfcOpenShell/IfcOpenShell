import json


def create_logfile(thelogfile, ifcbasename):

    logfile = open(thelogfile, "w")
    logfile.write("BIMTester log file\n")
    logfile.write("------------------\n\n")
    logfile.write("ifc base file name: {}\n".format(ifcbasename))
    logfile.close()


def append_logfile(thecontext, step):

    # step attributes (also these set by user) scope is the scenario
    # https://behave.readthedocs.io/en/latest/thecontext_attributes.html
    print("Step '{}' failed".format(step.name))

    # log file
    logfile = open(thecontext.thelogfile, "a")
    logfile.write("\n\nStep '{}' failed\n".format(step.name))
    if hasattr(thecontext, "falseelems"):
        logfile.write("{}\n".format(
            json.dumps(thecontext.falseelems, indent=4)
        ))
        if hasattr(thecontext, "falseprops"):
            logfile.write("{}\n".format(
                json.dumps(thecontext.falseprops, indent=4)
            ))
    logfile.close()
