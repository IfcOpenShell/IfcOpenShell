from behave import step

from ifcdata_methods import assert_schema
from utils import switch_locale

@step("Die IFC Daten müssen das {schema} Schema benutzen")
def step_impl(context, schema):
    switch_locale(context.localedir, "de")
    assert_schema(context, schema)
