import pytest

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
