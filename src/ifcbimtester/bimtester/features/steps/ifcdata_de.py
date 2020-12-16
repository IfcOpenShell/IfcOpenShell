from behave import step

from utils import assert_schema


# https://behave.readthedocs.io/en/latest/api.html#step-macro-calling-steps-from-other-steps
# https://stackoverflow.com/questions/46735425/how-to-only-show-failing-tests-from-behave
# https://community.osarch.org/discussion/comment/4533/#Comment_4533

@step("Die IFC Daten müssen das {schema} Schema benutzen")
def step_impl(context, schema):
    try:
        context.execute_steps(
            "* IFC data must use the {schema} schema".format(schema=schema)
        )
    except Exception:
        assert_schema(schema, context.schema)
        # TODO translate error
        # "Wir haben ein Schema {} erwartet, aber die Daten sind Schema (}"
