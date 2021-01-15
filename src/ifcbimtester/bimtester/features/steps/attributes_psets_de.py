from behave import step

import attributes_psets_methods as apm
from utils import switch_locale


the_lang = "de"


@step("An alle {ifc_class} Bauteile ist im PSet {pset} das Attribut {aproperty} angehängt")
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )
