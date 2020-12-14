from behave import step

# https://behave.readthedocs.io/en/latest/api.html#step-macro-calling-steps-from-other-steps


@step("Die IFC daten müssen das {schema} Schema benutzen")
def step_impl(context, schema):
    context.execute_steps(
        "* IFC data must use the {schema} schema".format(schema=schema)
    )
