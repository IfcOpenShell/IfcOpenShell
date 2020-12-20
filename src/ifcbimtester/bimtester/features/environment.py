import fileinput
import json
import os

from behave.model import Scenario


this_path = os.path.dirname(os.path.realpath(__file__))
out_path = os.path.join(this_path, "..")


def before_all(context):
    userdata = context.config.userdata
    context.ifcbasename = userdata["ifcbasename"]
    context.localedir = userdata.get("localedir")

    # do not break after a failed scenario
    # https://community.osarch.org/discussion/comment/3328/#Comment_3328
    continue_after_failed = userdata.getbool("runner.continue_after_failed_step", True)
    Scenario.continue_after_failed_step = continue_after_failed

    # keep out path
    context.outpath = out_path

    # set up my log file
    context.thelogfile = os.path.join(
        out_path,
        context.ifcbasename + ".log"
    )
    logfile = open(context.thelogfile, "w")
    logfile.write("BIMTester log file\n")
    logfile.write("------------------\n\n")
    logfile.write("ifc base file name: {}\n".format(context.ifcbasename))
    logfile.close()

    # set up smart view file
    # since bimtesterfc directory in tmp is removed on every run
    # the sm_file does not need to be explicit removed first
    context.smview_file = os.path.join(
        out_path,
        context.ifcbasename + ".bcsv"
    )
    create_zoom_smartview(
        context.smview_file,
        context.ifcbasename,
    )

    """
    # test before_all ...
    mytestlogfile = open(os.path.join(out_path, "zztest.txt"), "w")
    mytestlogfile.write("myenvironmenttest\n")
    mytestlogfile.write(this_path)
    mytestlogfile.close()
    """


"""
# https://stackoverflow.com/a/31545036
# https://behave.readthedocs.io/en/latest/tutorial.html#environmental-controls

# logging the behave way
# https://behave.readthedocs.io/en/latest/api.html#logging-setup
def before_all(context):
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini".
    context.config.setup_logging()
"""


def after_step(context, step):
    if step.status == "failed":

        # step attributes (also these set by user) scope is the scenario
        # https://behave.readthedocs.io/en/latest/context_attributes.html
        print("Step '{}' failed".format(step.name))

        # log file
        logfile = open(context.thelogfile, "a")
        logfile.write("\n\nStep '{}' failed\n".format(step.name))
        if hasattr(context, "falseelems"):
            logfile.write(
                "{}\n"
                .format(json.dumps(context.falseelems, indent=4))
            )
            if hasattr(context, "falseprops"):
                # print(context.falseprops[228]['Allplan Attributes']['Umbaukategorie'])
                # print(type(context.falseprops[228]['Allplan Attributes']['Umbaukategorie']))
                # <class 'ifcopenshell.entity_instance.entity_instance'>
                logfile.write(
                    "{}\n"
                    .format(json.dumps(context.falseprops, indent=4))
                )
        logfile.close()

        # smart view
        if hasattr(context, "falseguids"):
            # print(context.falseguids)

            append_zoom_smartview(
                context.smview_file,
                step.name,
                context.falseguids
            )


def create_zoom_smartview(sm_file, ifcbasename):

    smf = open(sm_file, "w")
    smf.write('<?xml version="1.0"?>\n')
    smf.write("<bimcollabsmartviewfile>\n")
    smf.write("    <version>5</version>\n")
    smf.write("    <applicationversion>Win - Version: 3.4 (build 3.4.13.559)</applicationversion>\n")
    smf.write("</bimcollabsmartviewfile>\n")
    smf.write("\n")
    smf.write("<SMARTVIEWSETS>\n")
    smf.write("    <SMARTVIEWSET>\n")
    smf.write("        <TITLE>BIMTester {}</TITLE>\n".format(ifcbasename))
    smf.write("        <DESCRIPTION></DESCRIPTION>\n")
    smf.write("        <GUID>a2ddfaf7-97f2-4519-aabd-f2d94f6b4d6b</GUID>\n")
    smf.write("        <MODIFICATIONDATE>2020-10-30T13:23:30</MODIFICATIONDATE>\n")
    smf.write("        <SMARTVIEWS>\n")
    smf.write("        </SMARTVIEWS>\n")
    smf.write("    </SMARTVIEWSET>\n")
    smf.write("</SMARTVIEWSETS>\n")
    smf.close()


def append_zoom_smartview(sm_file, step_name, false_elements_guid):

    # build the smartview string
    smview_string = "            <SMARTVIEW>\n"
    smview_string += (
        "                <TITLE>GUID filter, {}</TITLE>\n"
        .format(step_name)
    )
    smview_string += "{}\n".format(each_smartview_string_before)
    for guid in false_elements_guid:
        smview_string += (
            "{}{}{}\n".format(
                rule_string_before,
                guid,
                rule_string_after)
        )
    smview_string += "{}\n".format(each_smartview_string_after)

    # insert smartview string into file
    theline = "        </SMARTVIEWS>"
    newtext = smview_string + theline
    for line in fileinput.FileInput(sm_file, inplace=True):
        # the print replaces the line in the file
        # and add the line afterwards
        print(line.replace(theline, newtext), end="")


each_smartview_string_title = """            <SMARTVIEW>
                <TITLE>Filter GUID</TITLE>
                <DESCRIPTION></DESCRIPTION>"""


each_smartview_string_before = """                <CREATOR>bernd@bimstatik.ch</CREATOR>
                <CREATIONDATE>2020-10-30T13:18:45</CREATIONDATE>
                <MODIFIER>bernd@bimstatik.ch</MODIFIER>
                <MODIFICATIONDATE>2020-10-30T13:23:30</MODIFICATIONDATE>
                <GUID>15fda94f-b4bf-43be-8ef4-15d3121137e1</GUID>
                <RULES>
                    <RULE>
                        <IFCTYPE>Any</IFCTYPE>
                        <PROPERTY>
                            <NAME>None</NAME>
                            <PROPERTYSETNAME>None</PROPERTYSETNAME>
                            <TYPE>None</TYPE>
                            <VALUETYPE>None</VALUETYPE>
                            <UNIT>None</UNIT>
                        </PROPERTY>
                        <CONDITION>
                            <TYPE>Is</TYPE>
                            <VALUE></VALUE>
                        </CONDITION>
                        <ACTION>
                            <TYPE>AddSetColored</TYPE>
                            <R>187</R>
                            <G>187</G>
                            <B>187</B>
                        </ACTION>
                    </RULE>
                    <RULE>
                        <IFCTYPE>Any</IFCTYPE>
                        <PROPERTY>
                            <NAME>None</NAME>
                            <PROPERTYSETNAME>None</PROPERTYSETNAME>
                            <TYPE>None</TYPE>
                            <VALUETYPE>None</VALUETYPE>
                            <UNIT>None</UNIT>
                        </PROPERTY>
                        <CONDITION>
                            <TYPE>Is</TYPE>
                            <VALUE></VALUE>
                        </CONDITION>
                        <ACTION>
                            <TYPE>SetTransparent</TYPE>
                        </ACTION>
                    </RULE>"""


each_smartview_string_after = """                </RULES>
                <INFORMATIONTAKEOFF>
                    <PROPERTYSETNAME>None</PROPERTYSETNAME>
                    <PROPERTYNAME>None</PROPERTYNAME>
                    <OPERATION>0</OPERATION>
                </INFORMATIONTAKEOFF>
            </SMARTVIEW>"""


rule_string_before = """                    <RULE>
                        <IFCTYPE>Any</IFCTYPE>
                        <PROPERTY>
                            <NAME>GUID</NAME>
                            <PROPERTYSETNAME>Summary</PROPERTYSETNAME>
                            <TYPE>Summary</TYPE>
                            <VALUETYPE>StringValue</VALUETYPE>
                            <UNIT>None</UNIT>
                        </PROPERTY>
                        <CONDITION>
                            <TYPE>Is</TYPE>
                            <VALUE>"""


rule_string_after = """</VALUE>
                        </CONDITION>
                        <ACTION>
                            <TYPE>SetColored</TYPE>
                            <R>255</R>
                            <G>10</G>
                            <B>10</B>
                        </ACTION>
                    </RULE>"""
