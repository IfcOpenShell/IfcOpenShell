from behave import step

import attributes_psets_methods as apm
from utils import switch_locale


the_lang = "fr"


"""
# TODO the next line needs translation
@step("All {ifc_class} elements have an {aproperty} property in the {pset} pset")
def step_impl(context, ifc_class, aproperty, pset):
    switch_locale(context.localedir, the_lang)
    apm.eleclass_has_property_in_pset(
        context,
        ifc_class,
        aproperty,
        pset
    )
"""
