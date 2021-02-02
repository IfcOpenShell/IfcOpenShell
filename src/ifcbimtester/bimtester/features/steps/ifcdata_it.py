from behave import step


@step("I dati IFC devono seguire lo schema {schema}")
def step_impl(context, schema):
    context.execute_steps(f"* IFC data must use the {schema} schema")
