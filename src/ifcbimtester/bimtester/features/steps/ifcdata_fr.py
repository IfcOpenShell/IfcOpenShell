from behave import step

from ifcdata_methods import assert_schema
from utils import switch_locale

@step("Les données IFC doivent utiliser le schéma {schema}")
def step_impl(context, schema):
    switch_locale(context.localedir, "fr")
    assert_schema(context, schema)
