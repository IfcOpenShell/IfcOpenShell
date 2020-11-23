#!/usr/bin/env python3

# ***************************************************************************
# *   Copyright (c) 2020 Dion Moult <>                                      *
# *   Copyright (c) 2020 Bernd Hahnebach <bernd@bimstatik.org>              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

# Bernd: IMHO, this should go one lever up,
# or all other code should go one level down
# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3


# ATM bimtester code is copied here for for the sake of convenience
# TODO bimtester should be installed in conjunction with ifcopenshell
# to /urs/local by make install


# Unix:
# $ pyinstaller --onefile --clean --icon=icon.ico --add-data "features:features" bimtester.py`
# Windows:
# $ pyinstaller --onefile --clean --icon=icon.ico --add-data "features;features" bimtester.py`


import argparse

import clean
import reports
import run


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs unit tests for BIM data")
    parser.add_argument("-p", "--purge", action="store_true", help="Purge tests of deleted elements")
    parser.add_argument("-r", "--report", action="store_true", help="Generate a HTML report")
    parser.add_argument("-c", "--console", action="store_true", help="Show results in the console")
    parser.add_argument("-f", "--feature", type=str, help="Specify a feature file to test", default="")
    parser.add_argument(
        "-a", "--advanced-arguments", type=str, help="Specify your own arguments to Python's Behave", default=""
    )
    args = vars(parser.parse_args())

    if args["purge"]:
        clean.TestPurger().purge()
    elif args["report"]:
        reports.generate_report()
    else:
        run.run_tests(args)
    print("# All tasks are complete :-)")
