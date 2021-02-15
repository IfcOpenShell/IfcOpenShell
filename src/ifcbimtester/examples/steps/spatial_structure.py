from behave import step

from utils import IfcFile


@step("all buildings have an address")
def step_impl(context):
    for building in IfcFile.get().by_type("IfcBuilding"):
        if not building.BuildingAddress:
            assert False, f'The building "{building.Name}" has no address.'
