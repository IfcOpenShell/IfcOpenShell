#include "Converter.h"

#include "../../ifcgeom/schema_agnostic/IfcGeomElement.h"

ifcopenshell::geometry::Converter::Converter(const std::string& geometry_library, IfcParse::IfcFile* file, settings& s)
	: settings_(s)
{
	kernel_ = kernels::construct(geometry_library, file);
	mapping_ = impl::mapping_implementations().construct(file, settings_);
}

ifcopenshell::geometry::NativeElement* ifcopenshell::geometry::Converter::create_brep_for_representation_and_product(
	IfcUtil::IfcBaseEntity* representation, IfcUtil::IfcBaseEntity* product) {

	std::stringstream representation_id_builder;

	const std::string product_type = product->declaration().name();
	// @todo
	element_settings s(settings_, 1.0 /*getValue(GV_LENGTH_UNIT) */, product_type);

	int parent_id = -1;
	try {
		IfcUtil::IfcBaseEntity* parent_object = mapping_->get_decomposing_entity(product);
		if (parent_object) {
			parent_id = parent_object->data().id();
		}
	} catch (const std::exception& e) {
		Logger::Error(e);
	}

	const std::string guid = product->get_value<std::string>("GlobalId");
	const std::string name = product->get_value_or<std::string>("Name", "");
	
	representation_id_builder << representation->data().id();

	ifcopenshell::geometry::Representation::BRep* shape;
	ifcopenshell::geometry::ConversionResults shapes;

	/*
	auto rep_item = mapping_->map(representation);
	// @todo should map() throw an exception instead?
	if (rep_item == nullptr) {
		return nullptr;
	}
	*/


	std::clock_t map_start = std::clock();

	// @todo how to combine product_node and rep_item?
	auto product_node = (taxonomy::geom_item*) mapping_->map(product);
	if (product_node == nullptr) {
		return nullptr;
	}

	std::clock_t geom_start = std::clock();
	
	auto place = taxonomy::matrix4();
	std::swap(place, product_node->matrix);

	try {
		kernel_->convert(product_node, shapes);
	} catch (...) {
		std::ostringstream oss;
		product_node->print(oss);
		std::string s = oss.str();
		std::wcout << s.c_str() << std::endl;
		return nullptr;
	}

	shape = new ifcopenshell::geometry::Representation::BRep(s, representation_id_builder.str(), shapes);

	std::clock_t geom_end = std::clock();

	total_map_time += (geom_start - map_start) / (double) CLOCKS_PER_SEC;
	total_geom_time += (geom_end - geom_start) / (double) CLOCKS_PER_SEC;

	return new NativeElement(
		product->data().id(),
		parent_id,
		name,
		product_type,
		guid,
		// @todo
		"",
		place,
		// product_node->matrix,
		boost::shared_ptr<ifcopenshell::geometry::Representation::BRep>(shape),
		product
	);
	
	/*
	std::stringstream representation_id_builder;

	representation_id_builder << representation->data().id();

	ifcopenshell::geometry::kernels::Representation::BRep* shape;
	ifcopenshell::geometry::kernels::ConversionResults shapes;

	if (!convert_shapes(representation, shapes)) {
		return 0;
	}

	if (settings.get(IteratorSettings::APPLY_LAYERSETS)) {
		if (apply_layerset(product, shapes)) {

			IfcSchema::IfcRelAssociates::list::ptr associations = product->HasAssociations();
			for (IfcSchema::IfcRelAssociates::list::it it = associations->begin(); it != associations->end(); ++it) {
				IfcSchema::IfcRelAssociatesMaterial* associates_material = (**it).as<IfcSchema::IfcRelAssociatesMaterial>();
				if (associates_material) {
					unsigned layerset_id = associates_material->RelatingMaterial()->data().id();
					representation_id_builder << "-layerset-" << layerset_id;
					break;
				}
			}

		}
	}

	bool material_style_applied = false;

	const IfcSchema::IfcMaterial* single_material = get_single_material_association(product);
	if (single_material) {
		const ifcopenshell::geometry::kernels::SurfaceStyle* s = get_style(single_material);
		for (ifcopenshell::geometry::kernels::ConversionResults::iterator it = shapes.begin(); it != shapes.end(); ++it) {
			if (!it->hasStyle() && s) {
				it->setStyle(s);
				material_style_applied = true;
			}
		}
	} else {
		bool some_items_without_style = false;
		for (ifcopenshell::geometry::kernels::ConversionResults::iterator it = shapes.begin(); it != shapes.end(); ++it) {
			if (!it->hasStyle()) {
				some_items_without_style = true;
				break;
			}
		}
		if (some_items_without_style) {
			Logger::Warning("No material and surface styles for:", product);
		}
	}

	if (material_style_applied) {
		representation_id_builder << "-material-" << single_material->data().id();
	}

	ConversionResultPlacement* trsf = nullptr;
	try {
		convert_placement(product->ObjectPlacement(), trsf);
	} catch (const std::exception& e) {
		Logger::Error(e);
	} catch (...) {
		Logger::Error("Failed to construct placement");
	}

	// Does the IfcElement have any IfcOpenings?
	// Note that openings for IfcOpeningElements are not processed
	IfcSchema::IfcRelVoidsElement::list::ptr openings = find_openings(product)->as<IfcSchema::IfcRelVoidsElement>();

	const std::string product_type = product->declaration().name();
	ElementSettings element_settings(settings, getValue(GV_LENGTH_UNIT), product_type);

	if (!settings.get(ifcopenshell::geometry::kernels::IteratorSettings::DISABLE_OPENING_SUBTRACTIONS) && openings && openings->size()) {
		representation_id_builder << "-openings";
		for (IfcSchema::IfcRelVoidsElement::list::it it = openings->begin(); it != openings->end(); ++it) {
			representation_id_builder << "-" << (*it)->data().id();
		}

		ifcopenshell::geometry::kernels::ConversionResults opened_shapes;
		bool caught_error = false;
		try {
			convert_openings(product, openings, shapes, trsf, opened_shapes);
		} catch (const std::exception& e) {
			Logger::Message(Logger::LOG_ERROR, std::string("Error processing openings for: ") + e.what() + ":", product);
			caught_error = true;
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Error processing openings for:", product);
		}

		if (caught_error && opened_shapes.size() < shapes.size()) {
			opened_shapes = shapes;
		}

		if (settings.get(IteratorSettings::USE_WORLD_COORDS)) {
			for (ifcopenshell::geometry::kernels::ConversionResults::iterator it = opened_shapes.begin(); it != opened_shapes.end(); ++it) {
				it->prepend(trsf);
			}
			trsf = nullptr;
			representation_id_builder << "-world-coords";
		}
		shape = new ifcopenshell::geometry::kernels::Representation::BRep(element_settings, representation_id_builder.str(), opened_shapes);
	} else if (settings.get(IteratorSettings::USE_WORLD_COORDS)) {
		for (ifcopenshell::geometry::kernels::ConversionResults::iterator it = shapes.begin(); it != shapes.end(); ++it) {
			it->prepend(trsf);
		}
		trsf = nullptr;
		representation_id_builder << "-world-coords";
		shape = new ifcopenshell::geometry::kernels::Representation::BRep(element_settings, representation_id_builder.str(), shapes);
	} else {
		shape = new ifcopenshell::geometry::kernels::Representation::BRep(element_settings, representation_id_builder.str(), shapes);
	}

	std::string context_string = "";
	if (representation->hasRepresentationIdentifier()) {
		context_string = representation->RepresentationIdentifier();
	} else if (representation->ContextOfItems()->hasContextType()) {
		context_string = representation->ContextOfItems()->ContextType();
	}

	auto elem = new NativeElement<P, PP>(
		product->data().id(),
		parent_id,
		name,
		product_type,
		guid,
		context_string,
		trsf,
		boost::shared_ptr<ifcopenshell::geometry::kernels::Representation::BRep>(shape),
		product
	);

	if (settings.get(IteratorSettings::VALIDATE_QUANTITIES)) {
		validate_quantities(product, elem->geometry());
	}

	return elem;

	*/
}

ifcopenshell::geometry::NativeElement* ifcopenshell::geometry::Converter::create_brep_for_processed_representation(
	IfcUtil::IfcBaseEntity* /* representation */, IfcUtil::IfcBaseEntity* product,
	ifcopenshell::geometry::NativeElement* brep)
{
	int parent_id = -1;
	try {
		IfcUtil::IfcBaseEntity* parent_object = mapping_->get_decomposing_entity(product);
		if (parent_object) {
			parent_id = parent_object->data().id();
		}
	} catch (const std::exception& e) {
		Logger::Error(e);
	}

	const std::string guid = product->get_value<std::string>("GlobalId");
	const std::string name = product->get_value_or<std::string>("Name", "");

	auto placement = (taxonomy::geom_item*) mapping_->map(product);

	/*
	std::string context_string = "";
	if (representation->hasRepresentationIdentifier()) {
		context_string = representation->RepresentationIdentifier();
	} else if (representation->ContextOfItems()->hasContextType()) {
		context_string = representation->ContextOfItems()->ContextType();
	}
	*/

	const std::string product_type = product->declaration().name();

	return new NativeElement(
		product->data().id(),
		parent_id,
		name,
		product_type,
		guid,
		// @todo
		"",
		placement->matrix,
		brep->geometry_pointer(),
		product
		);
}

//#include "../../ifcparse/Ifc2x3.h"
//#include "../../ifcparse/Ifc4.h"
//
//// @todo remove
//#include "../../ifcgeom/schema_agnostic/opencascade/OpenCascadeConversionResult.h"
//
//#include <TopExp.hxx>
//#include <TopTools_ListOfShape.hxx>
//#include <TopTools_IndexedMapOfShape.hxx>
//#include <TopTools_IndexedDataMapOfShapeListOfShape.hxx>
//
//IfcGeom::Kernel::Kernel(const std::string& geometry_library, IfcParse::IfcFile* file) {
//	if (file != 0) {
//		if (file->schema() == 0) {
//			throw IfcParse::IfcException("No schema associated with file");
//		}
//
//		const std::string& schema_name = file->schema()->name();
//		implementation_ = impl::kernel_implementations().construct(schema_name, geometry_library, file);
//	}
//}
//
//int IfcGeom::Kernel::count(const ConversionResultShape* s_, int t_, bool unique) {
//	// @todo make kernel agnostic
//	const TopoDS_Shape& s = ((OpenCascadeShape*) s_)->shape();
//	TopAbs_ShapeEnum t = (TopAbs_ShapeEnum) t_;
//
//	if (unique) {
//		TopTools_IndexedMapOfShape map;
//		TopExp::MapShapes(s, t, map);
//		return map.Extent();
//	} else {
//		int i = 0;
//		TopExp_Explorer exp(s, t);
//		for (; exp.More(); exp.Next()) {
//			++i;
//		}
//		return i;
//	}
//}
//
//
//int IfcGeom::Kernel::surface_genus(const ConversionResultShape* s_) {
//	// @todo make kernel agnostic
//	const TopoDS_Shape& s = ((OpenCascadeShape*) s_)->shape();
//	OpenCascadeShape Ss(s);
//
//	int nv = count(&Ss, (int) TopAbs_VERTEX, true);
//	int ne = count(&Ss, (int) TopAbs_EDGE, true);
//	int nf = count(&Ss, (int) TopAbs_FACE, true);
//
//	const int euler = nv - ne + nf;
//	const int genus = (2 - euler) / 2;
//
//	return genus;
//}
//
//
//IfcUtil::IfcBaseEntity* IfcGeom::Kernel::get_decomposing_entity(IfcUtil::IfcBaseEntity* inst, bool include_openings) {
//	if (inst->as<Ifc2x3::IfcProduct>()) {
//		return get_decomposing_entity_impl(inst->as<Ifc2x3::IfcProduct>(), include_openings);
//	} else if (inst->as<Ifc4::IfcProduct>()) {
//		return get_decomposing_entity_impl(inst->as<Ifc4::IfcProduct>(), include_openings);
//	} else if (inst->declaration().name() == "IfcProject") {
//		return nullptr;
//	} else {
//		throw IfcParse::IfcException("Unexpected entity " + inst->declaration().name());
//	}
//}
//
//
//bool IfcGeom::Kernel::is_manifold(const ConversionResultShape* s_) {
//        // @todo make kernel agnostic
//        const TopoDS_Shape& a = ((OpenCascadeShape*) s_)->shape();
//
//	if (a.ShapeType() == TopAbs_COMPOUND || a.ShapeType() == TopAbs_SOLID) {
//		TopoDS_Iterator it(a);
//		for (; it.More(); it.Next()) {
//			OpenCascadeShape s(it.Value());
//			if (!is_manifold(&s)) {
//				return false;
//			}
//		}
//		return true;
//	} else {
//		TopTools_IndexedDataMapOfShapeListOfShape map;
//		TopExp::MapShapesAndAncestors(a, TopAbs_EDGE, TopAbs_FACE, map);
//
//		for (int i = 1; i <= map.Extent(); ++i) {
//			if (map.FindFromIndex(i).Extent() != 2) {
//				return false;
//			}
//		}
//
//		return true;
//	}
//}
