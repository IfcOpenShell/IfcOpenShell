def pytest_addoption(parser):
    parser.addoption(
        "--rule",
        action="store",
        default=None,
        help="Only run test_rules.py fixtures whose filename contains this substring.",
    )
