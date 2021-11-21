from behave import step
from behave import use_step_matcher

use_step_matcher("parse")


@step('Alle "{ifc_class}" Bauteile haben das Attribut "{aproperty}" im PSet "{pset}"')
def step_impl(context, ifc_class, aproperty, pset):
    context.execute_steps(f'* All "{ifc_class}" elements have an "{aproperty}" property in the "{pset}" pset')
