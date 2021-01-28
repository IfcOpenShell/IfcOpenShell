from behave import step

from utils import assert_attribute
from utils import IfcFile
from utils import switch_locale


the_lang = "de"


@step("Die Globale Identifikationskennung (Globally Unique Identifier = GUID) des Projektes ist {guid}")
def step_impl(context, guid):
    switch_locale(context.localedir, the_lang)
    assert_attribute(IfcFile.get().by_type("IfcProject")[0], "GlobalId", guid)


@step('Der Name, die Abkürzung oder die Kurzkennung des Projektes ist "{value}"')
def step_impl(context, value):
    switch_locale(context.localedir, the_lang)
    assert_attribute(IfcFile.get().by_type("IfcProject")[0], "Name", value)
