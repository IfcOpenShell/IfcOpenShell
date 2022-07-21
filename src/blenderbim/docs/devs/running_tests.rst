.. _blenderbim/running_tests:

Running tests
=============

The BlenderBIM Add-on has three layers of tests for each of its three technology
layers. These roughly form a test pyramid, moving from many abstract domain
logic tests, to low-level concrete unit tests, to a minimal number of UI and
smoke tests. These tests use ``pytest`` as the test framework and runner, so you
will need to install ``pytest``.

All development is expected to use test driven development, and so we expect
test coverage to be 100% where it is technically possible to test.

When running tests, Makefile targets are provided for convenience so you can
type in a simple command without knowing the internals.

Because the BlenderBIM Add-on depends on IfcOpenShell, it is advised to also run
tests for IfcOpenShell and its Python bindings, which is not covered in this
document.

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

    $ cd src/blenderbim/
    $ make test-core

Tool tests
----------

The tool layer tests actual concrete functions. You will need to install the
following dependencies:

* pytest-blender, accessible to your system's Python
* Blender executable, accessible to pytest-blender on your system's Python
  (e.g.  through the ``blender`` command in your path)
* pytest, accessible to your Blender Python
* pytest-bdd, accessible to your Blender Python

You can install the dependencies by running the ``scripts/setup_pytest.py``
script in Blender.

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

    $ cd src/blenderbim/
    $ make test-tool # Test everything
    $ make test-tool MODULE=foo # Only test a single module

BlenderBIM Add-on tests
-----------------------

The BIM layer acts as a full integration test. It is not possible to fully test
the UI, as we cannot reliably emit interface signals, nor read the interface as
a DOM of sorts. The best we can do is to call Blender operators as a smoke test,
and also check simple property and scene changes. It has the same dependencies
as the tool tests.

.. code-block:: bash

    $ cd src/blenderbim/
    $ make test-bim # Test everything
    $ make test-bim MODULE=foo # Only test a single module
