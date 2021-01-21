from behave import step

import ifcdata_methods as idm
from utils import switch_locale


the_lang = "de"


@given("Die IFC-Datei wurde durch einen Startparameter zur Verfügung gestellt")
def step_impl(context):
    switch_locale(context.localedir, the_lang)
    idm.provide_ifcfile_by_argument(context)


@step("Die IFC-Daten müssen das {schema} Schema benutzen")
def step_impl(context, schema):
    switch_locale(context.localedir, the_lang)
    idm.has_ifcdata_specific_schema(context, schema)
