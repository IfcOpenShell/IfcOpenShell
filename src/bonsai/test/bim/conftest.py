import pytest


class _FakePropsBase:
    """Base for parametric-edit PropertyGroup stand-ins used in lifecycle tests.

    The parametric-edit lifecycle mixins read/write a common contract:
    ``is_editing`` (bool), ``last_kwargs`` (dict | None — capture of the last
    data written via ``set_props_kwargs_from_ifc_data``),
    ``set_props_kwargs_from_ifc_data(data)``, and
    ``get_general_kwargs(convert_to_project_units=True)``. Per-type stand-ins
    (door, railing, roof) subclass this and add their own kwargs accessors
    and per-type fields."""

    def __init__(self, general: dict | None = None):
        self.is_editing = False
        self.last_kwargs: dict | None = None
        self.general = dict(general) if general is not None else {}

    def set_props_kwargs_from_ifc_data(self, data):
        self.last_kwargs = dict(data)

    def get_general_kwargs(self, convert_to_project_units=True):
        return dict(self.general)


def make_lifecycle_obj(props, *, name="obj"):
    """Build a ``bpy.types.Object`` stand-in for parametric-lifecycle tests.

    The mixin code under test reads ``obj.props`` (the PropertyGroup
    stand-in) and ``obj.name`` (used in error reports). ``spec=bpy.types.Object``
    catches typo'd attribute access at test time. ``bpy`` is imported inside
    the function so this conftest stays importable when bpy is absent."""
    from unittest import mock

    import bpy

    obj = mock.Mock(spec=bpy.types.Object, name=name)
    obj.props = props
    obj.name = name
    return obj


# pytest by default doesn't print steps and where it failed. Let's fix that.


@pytest.hookimpl
def pytest_bdd_before_scenario(request, feature, scenario):
    print(f"\033[94m# {feature.name}\033[0m")
    print(f"\033[94m## {scenario.name}\033[0m")


@pytest.hookimpl(tryfirst=True)
def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    print(f"\033[92m>>> {step.name}\033[0m")


@pytest.hookimpl(tryfirst=True)
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args):
    print(f"\033[1;91m>>> {step.name} <-- FAILED\033[0m")
