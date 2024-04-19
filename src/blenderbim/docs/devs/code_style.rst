Code style
============


Black code formatter
-------------------------------
For Python code formatting, we use `Black code formatter <https://pypi.org/project/black/>`__ with ``--line-length 120``.

``black`` can be installed using ``pip install black`` and files can be formatted with the following example command:

.. code-block:: bash

   black --line-length 120 src/blenderbim/blenderbim/bim/module/qto/operator.py

Using PowerShell, you can run the Black formatter on the last commit in the repository.
You can change ``~1`` to ``~n`` to affect ``n`` commits.

.. code-block:: powershell

   git diff HEAD HEAD~1 --name-only | where {$_ -like "*.py"} | foreach-object { start $_ && black --line-length 120 $_ }
