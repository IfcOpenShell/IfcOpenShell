from behave import step


@step('Les données IFC doivent utiliser le schéma "{schema}"')
def step_impl(context, schema):
    context.execute_steps(f'* IFC data must use the "{schema}" schema')
