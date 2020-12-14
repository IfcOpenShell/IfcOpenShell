from behave import step

# https://behave.readthedocs.io/en/latest/api.html#step-macro-calling-steps-from-other-steps


@step("Les données IFC doivent utiliser le schéma {schema}")
def step_impl(context, schema):
    context.execute_steps(
        "* IFC data must use the {aschema} schema".format(aschema=schema)
    )
