SVG [mustache](https://mustache.github.io/) templates that will be used for sheets and fill be filled with infromation from the sheet's IfcDocumentInformation attributes (e.g. Identification, Name, Revision, etc).

A `Revisions` list is also available for templates that want to render a
revision history table. It is populated from any older revisions attached to
the sheet via `IfcDocumentInformationRelationship` (see
`ifcopenshell.api.document.add_information`'s `parent` argument and
`ifcopenshell.util.document.get_revision_history`), ordered from the most
recent superseded revision to the oldest. Each item is the superseded
document's raw attribute dictionary (e.g. `Revision`, `Description`,
`CreationTime`), so a template can do:

```xml
{{#Revisions}}<tspan>{{Revision}} - {{Description}}</tspan>{{/Revisions}}
```

None of the stock A1/A2/A3 titleblocks currently draw a revision table (that
is a titleblock artwork/layout decision left to project-specific templates);
they only show the sheet's own current `{{Revision}}`.
