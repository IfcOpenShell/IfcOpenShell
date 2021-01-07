from behave import step

from ifcdata_methods import assert_schema
from utils import switch_locale


the_lang = "fr"


@step("Les données IFC doivent utiliser le schéma {schema}")
def step_impl(context, schema):
    switch_locale(context.localedir, the_lang)
    assert_schema(context, schema)
