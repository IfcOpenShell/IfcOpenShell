from behave import step, use_step_matcher

use_step_matcher("parse")


@step("An alle {ifc_class} Bauteile ist im PSet {pset} das Attribut {aproperty} angehängt")
def step_impl(context, ifc_class, aproperty, pset):
    context.execute_steps(f"all {ifc_class} elements have an {aproperty} property in the {pset} pset")
