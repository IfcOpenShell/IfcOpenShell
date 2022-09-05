import os
import sys
import argparse

from ifc4d.p6xer2ifc import P6XER2Ifc
from ifc4d.p62ifc import P62Ifc
from ifc4d.msp2ifc import MSP2Ifc
from ifc4d.pp2ifc import PP2Ifc
import ifcopenshell


parser  = argparse.ArgumentParser()
parser .add_argument('-f','--file', action='store', type=str, 
                        required=True, help="schedule file name to be parsed")
parser .add_argument('-s','--schedule', action='store', required=True,
                        type=str, help='file format as xer, p6xml, mspxml, pp')
parser .add_argument('-i', '--ifcfile', action='store', required=False,
                        type=str, help='ifc file name as string e.g. \"file.ifc\"')
parser .add_argument('-o', '--output', action='store', required=True,
                        type=str, help='ifc file name as string e.g. \"file.ifc\"')
args = parser .parse_args()

def get_file():
    ifcfile = None
    if args.ifcfile:
        ifcfile = ifcopenshell.open(args.ifcfile)
    elif args.output:
        ifc = ifcopenshell.file(schema='IFC4')
        ifc.create_entity("IfcWorkPlan")
        ifc.create_entity("IfcProject")
        ifc.write(args.output)
        ifcfile = ifcopenshell.open(args.output)
    else:
        ifcfile = None
    return ifcfile

if not args.ifcfile:
    print("You need to provide an ifc file to add schedule")
    print("Examples python ifc4d -i model.ifc -s xer -f schedule.xer -o newifc.ifc")
elif not args.output:
    print("an output file is required to save changes")
    print("python ifc4d -o newfile.ifc -s xer -f schedule.xer")

elif args.schedule== "xer":
    p6xer = P6XER2Ifc()
    p6xer.xer = args.file
    p6xer.output = args.output
    ifcfile = get_file()
    if ifcfile:
        p6xer.file = ifcfile
        p6xer.execute()
    else: raise Exception("No files provided for output")
elif args.schedule == "mspxml":
    msp = MSP2Ifc()
    msp.xml = args.file()
    msp.output = args.output
    ifcfile = get_file()
    if ifcfile:
        msp.file = ifcfile
        msp.execute()
elif args.schedule == "p6xml":
    p6xml = P62Ifc()
    p6xml.output = args.output
    p6xml.xml = args.file
    ifcfile = get_file()
    if ifcfile:
        p6xml.file = ifcopenshell.open(args.ifcfile)
        p6xml.execute()
elif args.schedule == "pp":
    pp = PP2Ifc()
    pp.output = args.output
    pp.pp = args.file
    ifcfile = get_file()
    if ifcfile:
        pp.file = ifcopenshell.open(args.ifcfile)
        pp.execute()
else:
    print("schedule type you selected is not implemented at the moment")

