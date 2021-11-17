from behave import step


@step('IFC-gegevens moeten het "{schema}" -schema gebruiken')
def step_impl(context, schema):
    context.execute_steps(f'* IFC data must use the "{schema}" schema')


@step('De projectnaam, code of korte ID moet "{value}"')
def step_impl(context, value):
    context.execute_steps(f'* The project name, code, or short identifier must be "{value}"')
