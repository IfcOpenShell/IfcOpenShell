from behave import step

import ifcdata_methods as idm
from utils import switch_locale


the_lang = "it"


@given("Il file IFC è stato fornito attraverso un argumento")
def step_impl(context):
    switch_locale(context.localedir, the_lang)
    idm.provide_ifcfile_by_argument(context)


@step("I dati IFC devono seguire lo schema {schema}")
def step_impl(context, schema):
    switch_locale(context.localedir, the_lang)
    idm.has_ifcdata_specific_schema(context, schema)
