from behave import step


@step('Es sind ausschliesslich "{ifc_classes}" Bauteile vorhanden')
def step_impl(context, ifc_classes):
    context.execute_steps(f'* There are exclusively "{ifc_classes}" elements only')


@step('Es sind keine "{ifc_class}" Bauteile vorhanden')
def step_impl(context, ifc_class):
    context.execute_steps(f'* There are no "{ifc_class}" elements')


@step('Aus folgendem Grund gibt es keine "{ifc_class}" Bauteile: {reason}')
def step_impl(context, ifc_class, reason):
    context.execute_steps(f'* There are no "{ifc_class}" elements because "{reason}"')


@step('Alle "{ifc_class}" Bauteilklassenattribute haben einen Wert')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements class attributes have a value')


@step('Bei allen "{ifc_class}" Bauteilen ist der Name angegeben')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements have a name given')


@step('Bei allen "{ifc_class}" Bauteilen ist die Beschreibung angegeben')
def step_impl(context, ifc_class):
    context.execute_steps(f'* All "{ifc_class}" elements have a description given')
