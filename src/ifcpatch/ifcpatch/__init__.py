#!/usr/bin/env python3
# This can be packaged into one executable with ./make.py

import ifcopenshell
import logging


def execute(args, is_library=None):
    logging.basicConfig(filename=args["log"], filemode="a", level=logging.DEBUG)
    logger = logging.getLogger("IFCPatch")
    print("# Loading IFC file ...")
    ifc_file = ifcopenshell.open(args["input"])
    print("# Loading patch recipe ...")
    recipes = getattr(__import__("ifcpatch.recipes.{}".format(args["recipe"])), "recipes")
    recipe = getattr(recipes, args["recipe"])
    patcher = recipe.Patcher(args["input"], ifc_file, logger, args["arguments"])
    print("# Patching ...")
    patcher.patch()
    ifc_file = getattr(patcher, "file_patched", patcher.file)
    if is_library is True:
        return ifc_file
    print("# Writing patched file ...")
    if not args["output"]:
        args["output"] = args["input"]
    if isinstance(ifc_file, str):
        with open(args["output"], "w") as text_file:
            text_file.write(ifc_file)
    else:
        ifc_file.write(args["output"])
    print("# All tasks are complete :-)")
