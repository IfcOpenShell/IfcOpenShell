Running tests
=============

Bonsai has three layers of tests for each of its three technology layers:

1. **Core tests**: abstract domain logic unit tests agnostic of Blender
2. **Tool tests**: low-level concrete unit tests dependent on Blender
3. **UI tests**: high-level integration UI and smoke tests dependent on Blender

These tests use ``pytest`` as the test framework and runner, so install it:

.. code-block:: bash

    pip install pytest

All development is expected to use test driven development, and so we expect
test coverage to be 100% where it is technically possible to test.

When running tests, Makefile targets are provided for convenience so you can
type in a simple command without knowing the internals. This means you can run
tests by using the ``make`` command.

Because Bonsai depends on IfcOpenShell, it is advised to also run tests for
IfcOpenShell and its Python bindings, which is not covered in this document.

Core tests
----------

The core layer tests are pure Python unit tests with no dependencies on Blender
or other modules. They are designed to be fast and easy to run as they test
purely abstract domain logic.

Although they are vanilla Python tests, they do not use the Python Mock module.
Instead, a lightweight ``Prophecy`` mocker class is used, which allows tests to
be written in a highly concise, expressive manner. For those coming from a
BDD background in Ruby's RSpec, PHP's PHPSpec, and PHP's Prophecy, this is very
similar.

.. code-block:: bash

    cd src/bonsai/
    make test-core
    # If you're on Windows, and don't want to use make, use:
    pytest -p no:pytest-blender test/core

Tool tests
----------

The tool layer tests actual concrete functions. You will need to install the
following dependencies:

* pytest-blender, accessible to your system's Python
* Blender executable, accessible to pytest-blender on your system's Python
  (e.g.  through the ``blender`` command in your path)

.. code-block:: bash

    pip install pytest-blender
    # Check that "Blender" is in your system's path
    blender

On Windows, you can add Blender to the system path by doing:

1. Open the start menu and launch **Control Panel** > **System** >  **Edit the
   system environment variables**
2. In the **System Properties** window, under the **Advanced** tab press
   **Environment Variables**. This will open a dialog showing a list of all your
   variables.
3. In the **System Variables** section select the entry named **Path**, and
   press **Edit...**. This will open a new dialog showing all the directories
   stored in the **Path** variable.
4. Press **New** and browse to the directory where your **blender.exe** is
   located, such as in ``C:\Program Files\Blender Foundation\Blender 3.2``.

In addition, you will need to install these dependencies for Blender:

* pytest, accessible to your Blender Python
* pytest-bdd, accessible to your Blender Python

You can install the dependencies by running the ``setup_pytest.py`` script in
Blender:

1. Launch Blender
2. Load ``src/bonsai/scripts/setup_pytest.py`` in the Blender text editor
3. Run the script by pressing ``Text > Run Script``.
4. Check the Blender console for any errors or success messages.

.. warning::

   The ``scripts/setup_pytest.py`` may not work for all operating systems and
   installation environments. In this case, you may be required to install the
   dependencies manually.

   Please be aware that some Blender may come packaged with its own Python,
   which may be separate to the Python installation on your system. Be sure to
   install the dependencies to the correct Python environment.

Then, run the tests. This will launch Blender headlessly and check the behaviour
of all concrete functions.

.. code-block:: bash

    cd src/bonsai/
    make test-tool # Test everything
    make test-tool MODULE=foo # Only test a single module
    # If you're on Windows, and don't want to use make, use:
    pytest test/tool # Test everything
    pytest test/tool/test_foo.py # Only test a single module

UI tests
--------

The UI layer acts as a full integration test.

Before running these tests, follow the instructions for running tool tests
above.

You will also need to enable the **Sun Position** add-on, as it is required to
test georeferencing features: ``Edit > Preferences > Add-ons`` and install
**Lighting: Sun Position**.

.. code-block:: bash

    cd src/bonsai/
    make test-bim # Test everything
    make test-bim MODULE=foo # Only test a single module
    # If you're on Windows, and don't want to use make, use:
    pytest test/bim # Test everything
    pytest test/bim -m "foo" ./ --maxfail=1 # Only test a single module

Code styling
------------

`Black <https://black.readthedocs.io/en/stable/index.html>`__ is used for code
formatting. The settings for black are configured in the ``pyproject.toml`` at
the project root. At the project root, just run:

.. code-block:: bash

    black .
