from behave import step

from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('All buildings have an address')
def step_impl(context):
    for building in IfcStore.file.by_type("IfcBuilding"):
        if not building.BuildingAddress:
            assert False, f'The building "{building.Name}" has no address.'
