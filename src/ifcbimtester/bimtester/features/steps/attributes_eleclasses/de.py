# BIMTester - OpenBIM Auditing Tool
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BIMTester.
#
# BIMTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BIMTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BIMTester.  If not, see <http://www.gnu.org/licenses/>.

from behave import step


@step('Es sind ausschliesslich "{ifc_classes}" Bauteile vorhanden')
def step_impl(context, ifc_classes):
    context.execute_steps(f'* There are exclusively "{ifc_classes}" elements only')


@step('Es sind keine "{ifc_class}" Bauteile vorhanden')
def step_impl(context, ifc_class):
    context.execute_steps(f'* There are no "{ifc_class}" elements')


@step('Aus folgendem Grund gibt es keine "{ifc_class}" Bauteile: {reason}')
def step_impl(context, ifc_class, reason):
    context.execute_steps(f'* There are no "{ifc_class}" elements because "{reason}"')


@step('Alle "{ifc_class}" Bauteilklassenattribute haben einen Wert')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements class attributes have a value')


@step('Bei allen "{ifc_class}" Bauteilen ist der Name angegeben')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements have a name given')


@step('Bei allen "{ifc_class}" Bauteilen ist die Beschreibung angegeben')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements have a description given')
