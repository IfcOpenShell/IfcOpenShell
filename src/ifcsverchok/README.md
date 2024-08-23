# IfcSverchok
**IfcSverchok**  is a [Sverchok](http://nortikin.github.io/sverchok/) plugin that allows you to create native IFC models alongside your parametric Sverchok geometry.

N.B.! IfcSverchok nodes are WIP. You can experience Blender crashes while using them, especially if you're undoing (ctrl/cmd-Z) something in the node tree.

## Packaged installation[](https://docs.ifcopenshell.org/ifcsverchok/installation.html#packaged-installation "Permalink to this headline")

IfcSverchok is packaged like a regular Blender add-on, so installation is the same as any other Blender add-on. [Download IfcSverchok here](https://github.com/IfcOpenShell/IfcOpenShell/releases/download/ifcsverchok-240417/ifcsverchok-240417.zip).

Like all Blender add-ons, they can be installed using `Edit > Preferences > Addons > Install > Choose Downloaded ZIP > Enable Add-on Checkbox`. You can enable add-ons permanently by using `Save User Settings` from the Addons menu.

Before installing, you will also need to [install Bonsai](https://bonsaibim.org/download.html) and install the latest version of [Sverchok](https://github.com/nortikin/sverchok) (v1.2).

## Nodes
List of nodes that have been tested to the best of ability (nodes not listed here are not considered ready for use). If you find bugs/unexpected behaviour in any of them, please open an issue or get in touch otherwise.

Most nodes have a help description, and input tooltips, that show show up when hovering over the "?"-icon and socket input respectively. 

| Node name                | Inputs                                                                            | Outputs                                           | Description                                                                                                                                                |
|--------------------------|-----------------------------------------------------------------------------------|---------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| IFC Create Entity        | - Names<br />   - Descriptions<br />  - IfcClass<br />  - Representations<br />  - Locations<br />  - Properties | - Entities Ids                                    | Create IFC Entity. Takes one or multiple inputs.<br /> If 'Representation(s)' is given, that determines number of output entities. Otherwise, 'Names' is used.   |
| IFC Read Entity          | - Entity Id                                                                       | - Id<br />  - is_a<br />  - Other entity attributes (dynamic) | Decompose an IfcEntity into its attributes. Takes one entity id as input, returns attribute values.                                                        |
| IFC BMesh to IFC Repr    | - Context type<br />  - Context identifier<br />  - Target View<br />  - Blender Objects            | - Representations<br />  - Locations                    | Blender mesh to IfcShapeRepresentation.  Takes one or multiple geometries.<br /> Deconstructs joined geometries and creates a separate representation for each.  |
| IFC Sverchok to IFC Repr | - Context type<br />  - Context identifier<br />  - Target View<br />  - Vertices<br />  - Edges<br />  - Faces | - Representations                                 | Sverchok geometry to IfcShapeRepresentation. Takes one or multiple nested lists of inputs.                                                                 |
| IFC Create Blender Shape | - Entity Id(s)                                                                    | - Blender Object(s)                               | Create Blender shape from IfcEntity Id. Takes one or multiple IfcEntity Ids.<br /> Creates shapes in scene and returns them in output socket.                    |
| IFC Add Spatial Element  | - Names<br />  - IfcClass<br />  - Elements                                                   | - Entity Id(s)                                    | Add IfcElements to an IfcSpatialElement. Takes one or multiple nested lists of inputs.<br /> Input can also be a (list of) spacial elements to be aggregated.    |
| IFC Write File           | - path                                                                            |                                                   | Writes active Ifc model to path. <br />N.B.! It's recommended to use the 'Write File' panel under the "IfcSverchok" tab instead.                                 |
| IFC Class Picker         | - IfcProduct (from drop-down)<br /> - IfcClass (from drop-down)                         | - IfcClass                                        | Pick an IfcClass from drop-down list.                                                                                                                      |
| IFC By Id                | - Id                                                                              | - Entities                                        | Get IfcElement by step id. Takes one or multiple step ids.                                                                                                 |
| IFC By Guid              | - Guid                                                                            | - Entities                                        | Get IfcElement by guid. Takes one or multiple guids.                                                                                                       |
| IFC By Type              | - IfcProduct (from drop-down)<br /> - IfcClass (from drop-down)<br /> - Custom IfcClass       | - Entities<br /> - Entity Ids                           | Get IFC element(s) in file by type.  Pick an IfcProduct and an IfcClass or give a custom IfcClass.                                                         |
| IFC Add Pset             | - Name<br />  - Properties<br />  - Element Ids                                               | - (Pset) Entities                              | Add a property set and corresponding properties, in a JSON key:value format, to IfcElements.                                                               |
| IFC Generate Guid        |                                                                                   | - Guid                                            | Generate a unique GUID.                                                                                                                                    |
| IFC Get Property         | - Entity Ids<br />  - Pset name<br />  - Prop name                                            | - Value                                           | Get the value of a property of an IfcEntity. Can take multiple entity ids.                                                                                 |
| IFC Get Attribute        | - Entity Ids<br />  - Attribute Name                                                    | - Value                                           | Get the value of an attribute of an IfcEntity. Can take multiple entities.                                                                                 |

### IfcSverchok panel
IfcSverchok creates a "IfcSverchok" tab in the Nodes panel. It includes a "Re-run all nodes" button that creates a fresh IFC File and a "Write File" button. It's recommended to re-run all nodes before saving the file either through the panel or the "Write File" node.

## Examples
### Parametric Facade
The sverchok model was kindly provided by Erindale Woodford [https://twitter.com/erindale_xyz](https://twitter.com/erindale_xyz). Check out the sverchok script and the resulting IFC model in the example_files folder.
The example model consists of columns, floors and parametric facade slats, arranged into three buildings with three storeys each.


#### Overview of the whole script
This is the whole script. Part on the left creates the parametric Sverchok model. Part on the right converts the model to native IFC elements.
![Alt text](./assets/parametric_facade1.png?raw=true)

#### Overview of the IFC part of the script
The IFC  of the script consists of four sections: columns, floors, slats and storeys/building.
![Alt text](./assets/parametric_facade2.png?raw=true)

#### Create columns
Columns begin as three blender objects, one for each storey. "Blender Mesh to IFC Repr" node is used to create an IfcRepresentation for each distinct Blender geometry. Joined geometries are split up, but the original nesting is preserved, which results in three nested lists 84 with 84 representation IDs each. 

These are then, together with locations, fed to the "Create Entity" node, which creates the same number of entities (here: IfcColumns) and outs them in the same shape as input. (The "By ID" node here only shows the first item of the, in total, 252 columns).
![Alt text](./assets/parametric_facade_columns.png?raw=true)

#### Create Floors
Floors are created in the same manner as columns. They also begin as three Blender objects (one pr storey), with three distinct geometries in each (one per building). Therefore nine representations and nine entities are created with the proper nesting. (The "By ID" node here only shows the first item of the, in total, nine slabs).
![Alt text](./assets/parametric_facade_floors.png?raw=true)

#### Create Slats
Slats are created from Sverchok geometries instead of Blender objects. There is no other reason for this, then to showcase an alternative method. As it can be seen, 353 representations and entities are created with the "Sverchok to IFC Repr" and "Create Entity" nodes.
![Alt text](./assets/parametric_facade_slats.png?raw=true)

#### Create Storeys and Building
Columns and floors are joined pr. storey and fed into the "Add Spatial Element" node, with the IfcClass "IfcBuildingStorey". This creates three storeys with unique names.
These storeys are then, together with slats, aggregated into an IfcBuilding using the same node.
![Alt text](./assets/parametric_facade_storeys.png?raw=true)

#### Saving the model
To save IFC model we have built, you simply need to navigate to the IfcSverchok tab in the node menu and, first, click on "IFC Re-run all nodes" and afterwards click on "Write File". 

Re-running all nodes will take a couple of seconds, depending on the size of the model. Re-running creates a fresh IFC model, and removes all the duplicated/unneeded IfcElements that were created while building the model.

In this example model, we have created both storeys and a building, but it's not stricly necessary with IfcSverchok. All orphaned elements and spatial elements (like IfcSpace or IfcBuildingStorey) will be put into a default building and site. So in this example, even though we didn't make an IfcSite, it will be created, and our building put into it, when writing the file.
![Alt text](./assets/exporting_ifc.png?raw=true)

#### Opening The Created IFC Model
Now we can open the created IFC model with any IFC viewer or program. Here it is opened with BlenderBIM.
![Alt text](./assets/imported_ifc.png?raw=true)

### Other examples

<details>
<summary>
<b>Miscellaneous examples</b>
</summary>
Miscellaneous examples that showcase the "Add Pset", "Get Attribute", "Get Property", "By Guid", "By Type" and "Read Entity" nodes.

![Alt text](./assets/other_examples1.png?raw=true)
</details>

<details>
<summary>
<b>Multiple Blender Mesh Geometries</b>
</summary>
This example shows the behaviour of the "Blender Mesh to IFC Repr" and "Create Entity" nodes when dealing with jagged list inputs.
The initial inputs are two Blender objects, one containing a single geometry, and one containing two geometries (that were joined).
"Blender Mesh to IFC Repr" node creates three IfcRepresentations and outputs them in the shape [[[repr_1], [repr_2]], [repr_3]].

The "Create Entity" node preserves the same shape. Notice that names and descriptions are (at least for now) only checked for uniqueness pr. object, so we have the name "testwall1" and description "descr1" repeating between the two objects. 

The output of "Create Enity" would look identical if only one name and one description was given as input.

![Alt text](./assets/other_examples2.png?raw=true)
</details>

<details>
<summary>
<b>Multiple Sverchok Geometries</b>
</summary>
Similarly, when we in this example convert two sets of three boxes ([[[box1], [box2], [box3]],[[box4], [box5], [box6]]]), we get six IfcRepresentations and entities with the original shape preserved.
Notice that the "By Id" node doesn't preserve input shape (at this point), since it should only be used for viewing.

![Alt text](./assets/other_examples3.png?raw=true)

</details>
