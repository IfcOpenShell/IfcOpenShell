Code style
============


Python code formatters
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


There is also `ruff` with some basic linter rules (checked automatically by the same Github workflow).
Which also helps maintaining consistency across the code base
and ensure new Python syntax doesn't break code on older Python versions.

``ruff`` can be installed using ``pip install ruff`` and files can be formatted with the following example commands:

.. code-block:: bash
   
   # Check issues for the entire repository.
   ruff check
   # Apply some automatic fixes, if available.
   ruff check --fix
   # Check only some specific file.
   ruff src/bonsai/bonsai/bim/module/qto/operator.py


Python code style
-------------------------------
Naming should be `PEP8 <https://www.python.org/dev/peps/pep-0008>`__ compliant.
Also prefer using long descriptive variable names.


C++ code style
-------------------------------

* prefer British English instead of American
* strictly use C++17
* use similar style for all languages
* spaces (4) instead of tabs
* `CONSTANTS_AND_MACROS`
* prefix macros that leak into client code (code using the IfcOpenShell libraries) with `IFC_`
* `filenames_namespaces_classes_functions_and_variables`
* `private_or_protected_member_variable_`
* postfix typedefs with `_t`, e.g. `typedef float real_t`
* (outdated? codebase is mainly using same line brace)
  K&R style braces for control flow, but braces on their own line for non-control flow
  (classes, enums, functions, etc.)

.. code-block:: c++

   #ifndef FOO_H
   #define FOO_H

   class foo
   {
   public:
      void bar(bool foo_or_bar)
      {
         if (foo_or_bar) {
               // ...
         } else {
               // ...
         }
      }

   private:
      bool i_am_foo_;
   }

   #endif
