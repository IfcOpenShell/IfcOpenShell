from behave import step


@step('Les données IFC doivent utiliser le schéma "{schema}"')
def step_impl(context, schema):
    context.execute_steps(f'* IFC data must use the "{schema}" schema')


@step('Nom du projet, son code ou un identifiant sommaire du type "{value}"')
def step_impl(context, value):
    context.execute_steps(f'* The project name, code, or short identifier must be "{value}"')
