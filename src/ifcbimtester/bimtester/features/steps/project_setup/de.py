from behave import step


@step('Die IFC-Daten müssen das "{schema}" Schema benutzen')
def step_impl(context, schema):
    context.execute_steps(f'* IFC data must use the "{schema}" schema')


@step('Die Globale Identifikationskennung (Globally Unique Identifier = GUID) des Projektes ist "{guid}"')
def step_impl(context, guid):
    context.execute_steps(f'* The project must have an identifier of "{guid}"')


@step('Der Name, die Abkürzung oder die Kurzkennung des Projektes ist "{value}"')
def step_impl(context, value):
    context.execute_steps(f'* The project name, code, or short identifier must be "{value}"')
