from behave import step

from geometric_detail_methods import class_geometric_representation
from utils import switch_locale


@step("Alle {ifc_class} Bauteile müssen eine geometrische Repräsentation der Klasse {representation_class} verwenden")
def step_impl(context, ifc_class, representation_class):
    switch_locale(context.localedir, "de")
    class_geometric_representation(context, ifc_class, representation_class)
