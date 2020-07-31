#!/usr/bin/env python3
# This can be packaged with `pyinstaller --onefile --clean --icon=icon.ico ifcpatch.py`

import ifcopenshell
import logging
import argparse

def execute(args, is_library=None):
    logging.basicConfig(filename=args['log'], filemode='a', level=logging.DEBUG)
    logger = logging.getLogger('IFCPatch')
    print('# Loading IFC file ...')
    ifc_file = ifcopenshell.open(args['input'])
    print('# Loading patch recipe ...')
    patcher = getattr(__import__('recipes.{}'.format(args['recipe'])), args['recipe']).Patcher(
            args['input'], ifc_file, logger, args['arguments'])
    print('# Patching ...')
    patcher.patch()
    if is_library is not None:
        return ifc_file
    print('# Writing patched file ...')
    if not args['output']:
        args['output'] = args['input']
    ifc_file.write(args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Patches IFC files to fix badly formatted data')
    parser.add_argument(
        '-i',
        '--input',
        type=str,
        required=True,
        help='The IFC file to patch')
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='The output file to save the patched IFC')
    parser.add_argument(
        '-r',
        '--recipe',
        type=str,
        required=True,
        help='Name of the recipe to use when patching')
    parser.add_argument(
        '-l',
        '--log',
        type=str,
        help='Specify a log file',
        default='ifcpatch.log')
    parser.add_argument(
        '-a',
        '--arguments',
        nargs='+',
        help='Specify custom arguments to the patch recipe')
    args = vars(parser.parse_args())

    execute(args)

    print('# All tasks are complete :-)')
