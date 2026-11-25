Python API Reference
====================

This page contains auto-generated API reference documentation [#f1]_.

.. toctree::
   :titlesonly:
   :maxdepth: 1

   {% for page in pages|selectattr("is_top_level_object") %}
   {{ page.include_path }}
   {% endfor %}

.. [#f1] Created with `sphinx-autoapi <https://github.com/readthedocs/sphinx-autoapi>`_
