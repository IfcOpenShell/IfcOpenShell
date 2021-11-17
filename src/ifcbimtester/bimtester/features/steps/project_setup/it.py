from behave import step


@step('I dati IFC devono seguire lo schema "{schema}"')
def step_impl(context, schema):
    context.execute_steps(f'* IFC data must use the "{schema}" schema')


@step('Il nome del progetto, codice o identificatore breve deve essere "{value}"')
def step_impl(context, value):
    context.execute_steps(f'* The project name, code, or short identifier must be "{value}"')
