#!/usr/bin/env python3
import argparse
import ifcpatch

parser = argparse.ArgumentParser(description="Patches IFC files to fix badly formatted data")
parser.add_argument("-i", "--input", type=str, required=True, help="The IFC file to patch")
parser.add_argument("-o", "--output", type=str, help="The output file to save the patched IFC")
parser.add_argument("-r", "--recipe", type=str, required=True, help="Name of the recipe to use when patching")
parser.add_argument("-l", "--log", type=str, help="Specify a log file", default="ifcpatch.log")
parser.add_argument("-a", "--arguments", nargs="+", help="Specify custom arguments to the patch recipe")
args = vars(parser.parse_args())
ifcpatch.execute(args)
