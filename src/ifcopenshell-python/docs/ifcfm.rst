IfcFM
=====

**Facility managers** (FM) need to know a lot of information about the building
in order to maintain the facility and its assets effectively. This includes
information about spaces, services, and key equipment, such as who to call when
things break, what the model number is, the warranty period, associated
certificates, what valve or circuit breaker must be shut off prior to
maintenance, and a punch list of periodic maintenance tasks.

Traditionally, this information is collected in numerous operations and
maintenance (O&M) manuals. IFC can collect this information incrementally
throughout the design development, construction, and commissioning stages of a
project. IFC's standardised and rich digital relationships can describe the
information that facility managers need. The most popular requirements
specification for IFC-based digital FM data is known as **COBie 2.4**.

Despite already requesting and receiving IFC deliverables, many clients still
request FM data in a spreadsheet format. Unfortunately, many of these
spreadsheet deliverables are not produced from IFC databases. This defeats the
purpose of BIM: asset data is no longer richly stored using international
standards and the BIM model may no longer be trusted.

IfcFM is a highly standards-compliant tool to convert FM data in IFC databases
to spreadsheets and other machine readable formats, such as ODS, XLSX, CSV,
Pandas, XML, and JSON. These formats may then be easily read, audited, or
imported into technologies that cannot work with IFC natively.

Supported data standards
------------------------

IfcFM assumes that you want to convert IFC data grouped into one or more
categories of data (e.g. list of assets, list of spare parts, list of documents
and certificates, etc). Each category of data includes a list or schedule of
information, and may reference information in other categories. In a
spreadsheet format, each category correlates to a worksheet, where each
worksheet focuses on one type of data  and has multiple columns (e.g. name of
manufacturer, point of contact, etc). There are four data standards compatible
with this data structure that IfcFM supports:

- **COBie 2.4**: the most popular requirements specification for FM data
  currently in use first published in 2007. It specifies requirements to
  collect almost 20 categories of data, focusing on maintainable equipment and
  finishes. It is published by the U.S. Army Corps of Engineers, National
  Building Information Model (NBIMS-US) standard, version 2, chapter 2.4, and
  in British Standard BS 1192-4:2014.
- **COBie 2.4 Legacy**: During the original development of **COBie 2.4**, a
  mapping to IFC was developed as part of the now unmaintained `COBie-plugins
  <https://github.com/opensourceBIM/COBie-plugins>`__ and loosely defined in
  Annex A with a number of ambiguities and oddities to accommodate the poor
  state of BIM vendors at the time. This preserves the original implementation.
- **COBie 3.0**: an update to **COBie 2.4** published by the National Building
  Information Model (NBIMS-US) standard. Unlike **COBie 2.4**, it is not a
  British Standard nor developed by the U.S. Army Corps of Engineers.
- **AOH-BSEM**: a draft specification by buildingSMART based on the lessons
  learned from the implementation of **COBie 2.4**, as part of a modular
  approach to asset data exchange that supports not just buildings, but
  infrastructure projects too. **AOH-BSEM** is set to supersede **COBIE 3.0**
  with a focus primarily on equipment maintenance.
- **Vanilla IFC**: Regardless of any "named" requirement such as above, IFC
  itself contains a number of standardised property sets and object types
  related to assets, warranties, manufacturers, and construction /
  installation. As expected, the majority of these are already referenced in
  named standards. "Vanilla" IFC offers a "specification agnostic" approach
  towards facility management data collection.

COBie 2.4 vs COBie 2.4 Legacy
-----------------------------

In collaboration with leading UK consultancy BuildData Group (formerly Bond
Bryan Digital), and inventor of COBie 2.4 Bill East (Prarie Sky Consulting), an
effort was made to preserve the original IFC mapping, as well as modernise the
mapping with the following goals:

1. For anyone delivering **COBie 2.4** data using best practices from graphical
   BIM software, there must be *no difference* between **COBie 2.4** and
   **COBie 2.4 Legacy**. It must not contradict any specifications in the
   official NBIMS-US and BS standards.
2. Update compatibility to IFC4X3.
3. Prioritise organisational data instead of personal data with discourage PII.
4. Prioritise bSI standardised property sets over custom ones.
5. Prevent needless repetition of data / fallback defaults that may result in
   invalid or unexpected data in obscure edge cases.
