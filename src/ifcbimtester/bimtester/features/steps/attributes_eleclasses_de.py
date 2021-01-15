from behave import step

import attributes_eleclasses_methods as aem
from utils import switch_locale


the_lang = "de"


@step("Es sind keine {ifc_class} Bauteile vorhanden")
def step_impl(context, ifc_class):
    switch_locale(context.localedir, the_lang)
    aem.no_eleclass(
        context,
        ifc_class
    )


@step("Aus folgendem Grund gibt es keine {ifc_class} Bauteile: {reason}")
def step_impl(context, ifc_class, reason):
    switch_locale(context.localedir, the_lang)
    aem.no_eleclass(
        context,
        ifc_class
    )


@step("Alle {ifc_class} Bauteilklassenattribute haben einen Wert")
def step_impl(context, ifc_class):
    switch_locale(context.localedir, the_lang)
    aem.eleclass_have_class_attributes_with_a_value(
        context,
        ifc_class
    )


@step("Bei allen {ifc_class} Bauteile ist der Name angegeben")
def step_impl(context, ifc_class):
    switch_locale(context.localedir, the_lang)
    aem.eleclass_has_name_with_a_value(
        context,
        ifc_class
    )


@step("Bei allen {ifc_class} Bauteile ist die Beschreibung angegeben")
def step_impl(context, ifc_class):
    switch_locale(context.localedir, the_lang)
    aem.eleclass_has_description_with_a_value(
        context,
        ifc_class
    )
