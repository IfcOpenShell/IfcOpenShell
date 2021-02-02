from behave import step


@step("Die IFC-Daten müssen das {schema} Schema benutzen")
def step_impl(context, schema):
    context.execute_steps(f"* IFC data must use the {schema} schema")
