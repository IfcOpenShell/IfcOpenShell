# bsdd

An experimental work in progress library to interact with the buildingSMART Data Dictionary (bSDD) API.

More reading:

 * [Swagger API docs](https://bs-dd-api-prototype.azurewebsites.net/swagger/index.html)
 * [bSDD Github Repository](https://github.com/buildingSMART/bSDD)

# Demo

Let's replicate the SketchUp example:

```
client = Client()
pprint(client.Domain())
pprint(client.SearchListOpen("http://identifier.buildingsmart.org/uri/nlsfb/nlsfb2005-2.2", RelatedIfcEntity="IfcWall"))
data = client.Classification("http://identifier.buildingsmart.org/uri/nlsfb/nlsfb2005-2.2/class/21.21")
pprint(data)
apply_ifc_classification_properties(ifc_file, element, data["classificationProperties"])
```
