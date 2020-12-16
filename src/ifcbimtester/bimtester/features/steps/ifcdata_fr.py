from behave import step

from utils import assert_schema


@step("Les données IFC doivent utiliser le schéma {schema}")
def step_impl(context, schema):
    try:
        context.execute_steps(
            "* IFC data must use the {schema} schema".format(schema=schema)
        )
    except Exception:
        assert_schema(schema, context.schema)
