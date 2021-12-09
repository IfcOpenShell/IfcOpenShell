import fileinput
import uuid


def create_zoom_set_of_smartviews(sm_file, smartviewset_name):

    # smartviewset_name: is the directory name in Zoom the SmartViews are in

    smf = open(sm_file, "w")
    smf.write('<?xml version="1.0"?>\n')
    smf.write("<bimcollabsmartviewfile>\n")
    smf.write("    <version>5</version>\n")
    smf.write("    <applicationversion>Win - Version: ")
    # next line belongs to last, because of line length
    smf.write("3.4 (build 3.4.13.559)</applicationversion>\n")
    smf.write("</bimcollabsmartviewfile>\n")
    smf.write("\n")
    smf.write("<SMARTVIEWSETS>\n")
    smf.write("    <SMARTVIEWSET>\n")
    smf.write("        <TITLE>BIMTester {}</TITLE>\n".format(smartviewset_name))
    smf.write("        <DESCRIPTION></DESCRIPTION>\n")
    smf.write("        <GUID>a2ddfaf7-97f2-4519-aabd-f2d94f6b4d6b</GUID>\n")
    smf.write("        <MODIFICATIONDATE>2020-10-30T13:23:30")
    # next line belongs to last, because of line length
    smf.write("</MODIFICATIONDATE>\n")
    smf.write("        <SMARTVIEWS>\n")
    smf.write("        </SMARTVIEWS>\n")
    smf.write("    </SMARTVIEWSET>\n")
    smf.write("</SMARTVIEWSETS>\n")
    smf.close()


def add_smartview(sm_file, smartview_name, guids):

    # smartview_name: is the name of the SmartView in Zoom
    # guids: List of guids
    # model will be grey and transparent, the guids objs will be red and not transparent

    # build the smartview string
    smview_string = "            <SMARTVIEW>\n"
    smview_string += (
        "                <TITLE>GUID filter, {}</TITLE>\n"
        .format(smartview_name)
    )
    smview_string += "{}\n".format(each_smartview_string_before1)
    smview_string += str(uuid.uuid4())  # create and add a smart view guid
    smview_string += "{}\n".format(each_smartview_string_before2)
    for guid in guids:
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


each_smartview_string_before1 = """                <CREATOR>bernd@bimstatik.ch</CREATOR>
                <CREATIONDATE>2020-10-30T13:18:45</CREATIONDATE>
                <MODIFIER>bernd@bimstatik.ch</MODIFIER>
                <MODIFICATIONDATE>2020-10-30T13:23:30</MODIFICATIONDATE>
                <GUID>"""


each_smartview_string_before2 = """</GUID>
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
