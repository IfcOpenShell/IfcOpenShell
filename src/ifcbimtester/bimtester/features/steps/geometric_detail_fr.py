from behave import step

import geometric_detail_methods as gdm
from utils import switch_locale


the_lang = "fr"


"""
# TODO the next line needs translation
@step("all {ifc_class} elements have an {representation_class} representation")
def step_impl(context, ifc_class, representation_class):
    switch_locale(context.localedir, the_lang)
    gdm.eleclass_has_geometric_representation_of_specific_class(
        context,
        ifc_class,
        representation_class
    )
"""
