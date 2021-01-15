from behave import step

import ifcdata_methods as idm
from utils import switch_locale


the_lang = "de"


@step("Die IFC Daten müssen das {schema} Schema benutzen")
def step_impl(context, schema):
    switch_locale(context.localedir, the_lang)
    idm.has_ifcdata_specific_schema(context, schema)
