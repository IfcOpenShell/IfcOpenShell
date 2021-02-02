from behave import step


@step("IFC-gegevens moeten het {schema} -schema gebruiken")
def step_impl(context, schema):
    context.execute_steps(f"* IFC data must use the {schema} schema")
