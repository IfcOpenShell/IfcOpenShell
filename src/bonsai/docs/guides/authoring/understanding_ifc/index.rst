=================
Understanding IFC
=================

Industry Foundation Classes (IFC) is an open, international standard for Building Information Modeling (BIM) data.
It provides a standardized way to describe, exchange, and share information about building and construction industry data.

IFC Schema
----------

The IFC schema defines a comprehensive set of consistent data representations of building information for exchange between AEC software applications.
It covers various aspects of buildings throughout their lifecycle, from conception to demolition.


buildingSMART and Standards
---------------------------

buildingSMART International (bSI) is the organization responsible for developing and maintaining the IFC standard.
They also develop other related standards like BCF (BIM Collaboration Format) and bSDD (buildingSMART Data Dictionary).

IfcOpenShell
------------

IfcOpenShell is the open-source software library used by Bonsai to read, write, and manipulate IFC files.
It provides the core functionality for working with IFC data.

Interoperability and Other Standards
------------------------------------

IFC is part of a broader ecosystem of open standards in the AEC industry. Other relevant standards include:

- COBie (Construction Operations Building Information Exchange)
- CityGML (City Geography Markup Language)
- gbXML (Green Building XML)

The use of open standards like IFC ensures interoperability between different software tools
and preserves data integrity throughout the building lifecycle.


Key Concepts
============

This section provides an overview of key IFC concepts and how they're implemented in Bonsai.


.. only:: builder_html and (not singlehtml)

   .. container:: toc-cards

      .. container:: card

         :doc:`spatial_objects`
            Basic spatial objects.

      .. container:: card

         :doc:`classification_and_types`
            IFC classification hierarchy and the concept of types and occurrences.

      .. container:: card

         :doc:`geometry_and_representations`
            Understanding IFC geometry, representations, and parametric materials.

      .. container:: card

         :doc:`working_with_representations`
            Representations in Bonsai.

.. container:: global-index-toc

   .. toctree::
      :hidden:
      :caption: Understanding IFC
      :maxdepth: 2

      spatial_objects
      classification_and_types
      geometry_and_representations
      working_with_representations
