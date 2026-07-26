Getting Started with IFC parsing
================================

The basis of all parsing and getting information from the IFC starts with obtaining a ``IfcParse::IfcFile`` object and validating that it is good for use.

.. code-block:: c++

    std::string input_file_path = "/path/to/my/model.ifc";
    IfcParse::IfcFile file(input_file_path);
    if (!file.good()) {
      std::cerr << "Unable to parse .ifc file" << std::endl;
      return 1;
    }

.. _schema-agnostic-parsing-of-ifcs:

Schema-agnostic parsing of IFCs
-------------------------------

It is advisable to design your programme in a schema-agnostic fashion to be able to process all schema versions of input IFCs. 
While different options are presented `here <http://blog.ifcopenshell.org/2019/12/v060.html>`__, the most comfortable approach for modern C++ developers
would be with the use of templates as shown below.

.. code-block:: c++
    
    // necessary includes

    // For BOOST_PP_SEQ_FOR_EACH and BOOST_PP_STRINGIZE preprocessor macro
    #include <boost/preprocessor/seq/for_each.hpp>
    // Include all possible schema types that could be parsed
    #include "ifcparse/Ifc2x3.h"
    #include "ifcparse/Ifc4.h"
    #include "ifcparse/Ifc4x3_add2.h"

    #define IFC_SCHEMA_SEQ (4x3_add2)(4)(2x3) // TODO: Enumerate through all IFC schemas you want to be able to process
    #define EXPAND_AND_CONCATENATE(elem) Ifc##elem
    #define PROCESS_FOR_SCHEMA(r, data, elem) if (schema_version == BOOST_PP_STRINGIZE(elem)) { parseIfc<EXPAND_AND_CONCATENATE(elem)>(file); } else

    template<typename Schema>
    void parseIfc(IfcParse::IfcFile &file) {
        const typename Schema::IfcProduct::list::ptr elements = file.instances_by_type<typename Schema::IfcProduct>();
        for (typename Schema::IfcProduct::list::it it = elements->begin();
            it != elements->end(); ++it) {
            Schema::IfcProduct *ifcProduct = *it;
            // TODO: Do something with ifcProduct
        }
    }

    void process(const std::string &schema_version, IfcParse::IfcFile &file) {
        // Syntactic sugar for iterating through all IFC schemas and passing them to main processing method
        BOOST_PP_SEQ_FOR_EACH(PROCESS_FOR_SCHEMA, ,IFC_SCHEMA_SEQ)
        { // The final else to catch unhandled schema version
            throw std::invalid_argument("IFC Schema " + schema_version + " not supported");
        }
    }

    int main(int argc, char* argv[]) {
        // file of IfcParse::IfcFile previously defined
        auto schema_version = file.schema()->name();
        schema_version = schema_version.substr(3);
        std::transform(schema_version.begin(), schema_version.end(), schema_version.begin(), [](unsigned char c) { return std::tolower(c); });
        process(schema_version, file);
        // TODO: Handle more cases of IFC schema versions here
    }

Reading out attributes of an IfcProduct
---------------------------------------

The properties of an ``IfcProduct``, and by extension any derived class, can be read as by calling the method of the same name, e.g. ``GlobalId()``, ``Name()``. 
Note that optional properties like name, long name, or description, among others, are wrapped with a ``boost::optional`` (`documentation <https://www.boost.org/doc/libs/1_84_0/libs/optional/doc/html/index.html>`__) container object. Except for pointer types such as IfcRoot::OwnerHistory, here the developer is still responsible for performing comparison to `nullptr` before using the value.

Navigating relationships in IFC
-------------------------------

While it is natural to look at the IFC format as a representation of a physical building model where physical objects are related to each other in a tree structure (e.g. site > building > storey > slab),
the IFC format allows for the representation of information in a graph-like manner, joining physical objects to meta-information through relationships. 
A detailed explanation of relationships in IFC is provided in this `blog post <https://constructingdata.wordpress.com/2018/04/09/ifc-for-the-layman-part-3-relationships/>`__. 

The following function shows how property sets can be extracted from a given ``IfcObject``. 

.. code-block:: c++

    template<typename Schema>
    void extractPropertySets(const typename Schema::IfcObject &obj,
                     typename std::vector<typename Schema::IfcPropertySet *> &property_sets) {
        const auto &is_defined_by = obj.IsDefinedBy();
        if (is_defined_by == nullptr)
            return;
        std::vector<typename Schema::IfcRelDefines *> rels(is_defined_by->size());
        typename std::vector<typename Schema::IfcRelDefines *>::iterator it = std::copy_if(
            is_defined_by->begin(), is_defined_by->end(), rels.begin(),
            [](const typename Schema::IfcRelDefines *x) {
                if (x == nullptr) return false;
                const typename Schema::IfcRelDefinesByProperties *defines_by_properties = 
                    x->template as<typename Schema::IfcRelDefinesByProperties>();
                if (defines_by_properties == nullptr) return false;
                const auto *relating_property_definition =
                    defines_by_properties->RelatingPropertyDefinition();
                if (relating_property_definition == nullptr) return false;
                return relating_property_definition->template as<typename Schema::IfcPropertySet>() !=
                    nullptr;
            });
        rels.resize(std::distance(rels.begin(), it));
        property_sets.resize(rels.size());
        std::transform(rels.begin(), rels.end(), property_sets.begin(),
                        [](const typename Schema::IfcRelDefines *x) {
                        const typename Schema::IfcRelDefinesByProperties *defines_by_properties = x->template as<typename Schema::IfcRelDefinesByProperties>();
                        return defines_by_properties->RelatingPropertyDefinition()->template as<typename Schema::IfcPropertySet>();
                        });
    }

Reading properties and quantities from an element
---------------------------------------------------

A frequent point of confusion is that ``IsDefinedBy()`` does *not* return the property set
or quantity set itself. It is an inverse attribute that lists every
``IfcRelDefinesByProperties`` relationship pointing at the element, and the relationship
still needs to be unwrapped via ``RelatingPropertyDefinition()`` to reach the actual
``IfcPropertySet`` (regular properties) or ``IfcElementQuantity`` (physical quantities such
as length, area, or volume). Both classes derive from ``IfcPropertySetDefinition``, so a
single cast check tells you which one you got:

.. code-block:: c++

    for (auto& rel : *element.IsDefinedBy()) {
        // IsDefinedBy() can also contain IfcRelDefinesByType, IfcRelDefinesByObject, or
        // IfcRelDefinesByTemplate relationships, so filter for the one we want first.
        auto* defines_by_props = rel->as<Ifc4::IfcRelDefinesByProperties>();
        if (!defines_by_props)
            continue;

        // This is the step that's easy to miss: the relationship is not the pset.
        auto* pset_def = defines_by_props->RelatingPropertyDefinition();

        if (auto* pset = pset_def->as<Ifc4::IfcPropertySet>()) {
            for (auto* prop : *pset->HasProperties()) {
                if (auto* single = prop->as<Ifc4::IfcPropertySingleValue>()) {
                    std::cout << single->Name() << " = "
                              << single->NominalValue()->data().toString() << std::endl;
                }
            }
        } else if (auto* qto = pset_def->as<Ifc4::IfcElementQuantity>()) {
            for (auto* quantity : *qto->Quantities()) {
                if (auto* length = quantity->as<Ifc4::IfcQuantityLength>()) {
                    std::cout << length->Name() << " = " << length->LengthValue() << std::endl;
                }
                // IfcQuantityArea, IfcQuantityVolume, IfcQuantityWeight, IfcQuantityCount,
                // and IfcQuantityTime all follow the same pattern.
            }
        }
    }

There is a second, easily-missed source of properties: the element's **type**. Properties
assigned to a type (e.g. a shared "IfcDuctSegmentType") apply to every element of that type,
and are reached completely differently, through ``IsTypedBy()`` and then
``RelatingType()->HasPropertySets()`` directly, with no relationship to unwrap:

.. code-block:: c++

    auto* typed_by = element.IsTypedBy();
    if (typed_by && typed_by->size()) {
        // Unlike IsDefinedBy(), a type only ever has one IfcRelDefinesByType relationship.
        auto* type = (*typed_by->begin())->RelatingType();
        if (auto* psets = type->HasPropertySets()) {
            for (auto* pset_def : *psets) {
                // pset_def can again be either an IfcPropertySet or an IfcElementQuantity,
                // and is handled exactly as above.
                std::cout << pset_def->data().toString() << std::endl;
            }
        }
    }

A complete, compilable example that ties both paths together for a chosen element (here
``IfcDuctSegment``, but any IFC class works the same way) looks like this:

.. code-block:: c++

    #include <ifcparse/IfcFile.h>
    #include <ifcparse/Ifc4.h>
    #include <iostream>

    void print_pset_or_qto(Ifc4::IfcPropertySetDefinition* pset_def) {
        if (auto* pset = pset_def->as<Ifc4::IfcPropertySet>()) {
            for (auto* prop : *pset->HasProperties()) {
                if (auto* single = prop->as<Ifc4::IfcPropertySingleValue>()) {
                    std::cout << "  " << single->Name() << " = "
                              << single->NominalValue()->data().toString() << std::endl;
                }
            }
        } else if (auto* qto = pset_def->as<Ifc4::IfcElementQuantity>()) {
            for (auto* quantity : *qto->Quantities()) {
                if (auto* length = quantity->as<Ifc4::IfcQuantityLength>()) {
                    std::cout << "  " << length->Name() << " = " << length->LengthValue() << std::endl;
                }
            }
        }
    }

    int main(int argc, char** argv) {
        if (argc < 2) {
            std::cerr << "Usage: " << argv[0] << " <model.ifc>" << std::endl;
            return 1;
        }

        IfcParse::IfcFile file(argv[1]);
        if (!file.good()) {
            std::cerr << "Unable to parse .ifc file" << std::endl;
            return 1;
        }

        auto duct_segments = file.instances_by_type<Ifc4::IfcDuctSegment>();
        if (duct_segments->size() == 0) {
            std::cerr << "No IfcDuctSegment instances found" << std::endl;
            return 1;
        }

        Ifc4::IfcDuctSegment* element = *duct_segments->begin();
        std::cout << "Inspecting " << element->Name().get_value_or("<unnamed>") << std::endl;

        // 1. Properties and quantities attached directly to the element instance.
        std::cout << "Element-level property sets:" << std::endl;
        for (auto& rel : *element->IsDefinedBy()) {
            if (auto* defines_by_props = rel->as<Ifc4::IfcRelDefinesByProperties>()) {
                print_pset_or_qto(defines_by_props->RelatingPropertyDefinition());
            }
        }

        // 2. Properties and quantities inherited from the element's type, if any.
        std::cout << "Type-level property sets:" << std::endl;
        auto* typed_by = element->IsTypedBy();
        if (typed_by && typed_by->size()) {
            auto* type = (*typed_by->begin())->RelatingType();
            if (auto* psets = type->HasPropertySets()) {
                for (auto* pset_def : *psets) {
                    print_pset_or_qto(pset_def);
                }
            }
        }

        return 0;
    }

.. note::

    The example above hardcodes the ``Ifc4`` namespace for readability. See
    :ref:`Schema-agnostic parsing of IFCs<schema-agnostic-parsing-of-ifcs>` above for how to
    write the same logic so it works against any schema version at once.

Defensive programming with IfcOpenshell
---------------------------------------

The need for (down-)casting object pointers when accessing various properties in an IFC entity is evident from the previous code sample as the methods and properties usually 
return the abstract class of the entity. It is hence important to check for ``nullptr`` when performing such casts. 
The existence of certain fields and properties should also be checked.  Also note that IfcOpenShell has as of now not been tested explicitly against malicious inputs. Schema validation (the correctness of attribute types and conformance to schema where rules) can currently only be assessed in Python (using `ifcopenshell.validate --rules`).
