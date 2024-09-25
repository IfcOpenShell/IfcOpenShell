Code style
============


Black code formatter
-------------------------------
For Python code formatting, we use `Black code formatter <https://pypi.org/project/black/>`__, 
black settings are stored in the repository's pyproject.toml.

We have GitHub workflow `ci-black-formatting` to maintain black formatting across the repository.

``black`` can be installed using ``pip install black`` and files can be formatted with the following example command:

.. code-block:: bash

   # Format the entire repository.
   # Should be used in 99% cases as the entire repository is already formatted using black.
   black .
   # Format only some specific file.
   black src/bonsai/bonsai/bim/module/qto/operator.py

