/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#include "../../../src/ifcparse/IfcHdf5File.h"
#include "../../../src/ifcgeom/IfcGeom.h"
#include "../../../src/ifcparse/IfcWritableEntity.h"

#include <Bnd_Box.hxx>
#include <BRepBndLib.hxx>

#include <algorithm>

#include "multifile_instance_locator.h"

void generate_bounding_boxes(IfcParse::IfcFile& f, const std::string& fn) {
	IfcGeom::Kernel kernel;
	auto unit_factor = kernel.initializeUnits(*f.entitiesByType<IfcSchema::IfcUnitAssignment>()->begin());
	
	IfcSchema::IfcProductDefinitionShape::list::ptr defs_ = f.entitiesByType<IfcSchema::IfcProductDefinitionShape>();
	std::vector<IfcSchema::IfcProductDefinitionShape*> defs(defs_->begin(), defs_->end());
	// Make sure to sort by id to have new definitions lining up in the same order
	std::sort(defs.begin(), defs.end(), [](IfcSchema::IfcProductDefinitionShape* a, IfcSchema::IfcProductDefinitionShape* b) {
		return a->data().id() < b->data().id();
	});

	std::ofstream str(fn.c_str(), std::ios_base::binary);

	int N = defs.size(), n = 0;

	std::cerr << "boxes:" << std::endl;

	std::for_each(defs.begin(), defs.end(), [&kernel, &str, N, &n, &unit_factor](IfcSchema::IfcProductDefinitionShape* def) {
		Bnd_Box box;
		auto reps = def->Representations();
		IfcSchema::IfcRepresentationContext* context;

		std::for_each(reps->begin(), reps->end(), [&kernel, &box, &context](auto rep) {
			IfcGeom::IfcRepresentationShapeItems items;

			if (rep->RepresentationIdentifier() == "Body") {
				kernel.convert(rep, items);
				context = rep->ContextOfItems();
			}

			for (auto& i : items) {
				BRepBndLib::AddClose(i.Shape(), box);
			}
		});

		const size_t name = def->data().id();

		double xyz[6];
		box.Get(xyz[0], xyz[1], xyz[2], xyz[3], xyz[4], xyz[5]);

		for (int i = 0; i < 6; ++i) {
			xyz[i] *= unit_factor.second;
		}

		str.write((char*)&name, sizeof(size_t));
		str.write((char*)xyz, sizeof(double) * 6);

		if (n++ % 1000 == 0) {
			std::cerr << "\r" << n * 100 / N << std::flush;
		}
	});

	std::cerr << std::endl;
}


void find_geometric_types(IfcParse::IfcFile& f, const std::string& tfn) {
	std::ofstream str(tfn.c_str(), std::ios_base::binary);

	IfcSchema::IfcProductDefinitionShape::list::ptr defs_ = f.entitiesByType<IfcSchema::IfcProductDefinitionShape>();
	std::vector<IfcSchema::IfcProductDefinitionShape*> defs(defs_->begin(), defs_->end());
	// Make sure to sort by id to have new definitions lining up in the same order
	std::sort(defs.begin(), defs.end(), [](IfcSchema::IfcProductDefinitionShape* a, IfcSchema::IfcProductDefinitionShape* b) {
		return a->data().id() < b->data().id();
	});

	std::set<IfcSchema::Type::Enum> geometric_types{ IfcSchema::Type::IfcStyledItem, IfcSchema::Type::IfcMaterialDefinitionRepresentation, IfcSchema::Type::IfcStyledRepresentation };
	std::set<IfcSchema::Type::Enum> other_types;

	std::set<IfcUtil::IfcBaseClass*> geometric_instances;

	for (auto ty : geometric_types) {
		auto insts = f.entitiesByType(ty);
		std::for_each(insts->begin(), insts->end(), [&geometric_instances](IfcUtil::IfcBaseClass* inst) {
			geometric_instances.insert(inst);
		});
	}

	int N, n;

	auto vist_geometric = [&f, &geometric_types, &geometric_instances, &N, &n](IfcUtil::IfcBaseEntity* def) {
		auto refs = f.traverse(def);
		geometric_instances.insert(refs->begin(), refs->end());
		std::for_each(refs->begin(), refs->end(), [&geometric_types](IfcUtil::IfcBaseClass* inst) {
			if (inst->declaration().as_entity()) {
				geometric_types.insert(inst->declaration().type());
			}
		});
		if (n++ % 1000 == 0) {
			std::cerr << "\r" << (n * 100 / N) << std::flush;
		}
	};

	n = 0; 
	N = defs.size();
	
	std::for_each(defs.begin(), defs.end(), vist_geometric);

	auto connection_geom = f.entitiesByType<IfcSchema::IfcConnectionGeometry>();
	
	n = 0;
	N = connection_geom->size();
	
	std::for_each(connection_geom->begin(), connection_geom->end(), vist_geometric);

	std::function<void(IfcUtil::IfcBaseClass*, IfcUtil::IfcBaseClass*)> fn;
	fn = [&f, &geometric_instances, &other_types, &fn](IfcUtil::IfcBaseClass* root, IfcUtil::IfcBaseClass* inst) {
		if (geometric_instances.find(inst) == geometric_instances.end()) {
			auto ty = inst->declaration().type();
			if (ty == IfcSchema::Type::IfcExtrudedAreaSolid) {
				std::cerr << inst->data().toString() << " reachded by " << root->data().toString() << std::endl;
			}

			// Not referenced. Revit generates unused IfcExtrudedAreaSolids some times.
			auto invs = f.getInverse(inst->data().id(), IfcSchema::Type::UNDEFINED, -1);
			if (root == inst && invs->size() == 0) {
				return;
			}

			other_types.insert(ty);
			auto refs = f.traverse(inst, 1);
			std::for_each(refs->begin() + 1, refs->end(), [&fn, root](IfcUtil::IfcBaseClass* inst) {
				if (inst->declaration().as_entity()) {
					fn(root, inst);
				}
			});
		}
	};

	N = std::distance(f.begin(), f.end());
	n = 0;

	std::for_each(f.begin(), f.end(), [&fn, N, &n](const auto& pair) {
		fn(pair.second, pair.second);
		if (n++ % 1000 == 0) {
			std::cerr << "\r" << n * 100 / N << std::flush;
		}
	});

	std::set<IfcSchema::Type::Enum> only_geometric;
	std::set_difference(geometric_types.begin(), geometric_types.end(),
		other_types.begin(), other_types.end(),
		std::inserter(only_geometric, only_geometric.begin()));

	only_geometric.erase(IfcSchema::Type::IfcGeometricRepresentationContext);

	std::cerr << "\nOnly geometric:" << std::endl;

	for (auto ty : only_geometric) {
		std::cerr << IfcSchema::Type::ToString(ty) << std::endl;
		const size_t name = ty;
		str.write((char*)&name, sizeof(size_t));
	}

	std::cin.get();
}

int main(int argc, char** argv) {
	const std::string cache_fn = argv[1] + std::string(".boxes.bin");
	const std::string types_fn = argv[1] + std::string(".types.bin");

	if (argc == 2 && !ifstream(cache_fn).good()) {
		std::string command = std::string("\"\"") + argv[0] + "\" \"" + argv[1] + "\" -b\"";
		if (system(command.c_str()) != 0) {
			return 1;
		}
	}

	if (argc == 2 && !ifstream(types_fn).good()) {
		std::string command = std::string("\"\"") + argv[0] + "\" \"" + argv[1] + "\" -t\"";
		if (system(command.c_str()) != 0) {
			return 1;
		}
	}

	IfcParse::IfcFile f;
	f.Init(argv[1]);

	if (argc == 3 && std::string(argv[2]) == "-b") {
		generate_bounding_boxes(f, cache_fn);
		return 0;
	}

	if (argc == 3 && std::string(argv[2]) == "-t") {
		find_geometric_types(f, types_fn);
		return 0;
	}

	std::set<IfcSchema::Type::Enum> only_geometric;
	{
		std::ifstream str(types_fn.c_str(), std::ios_base::binary);
		while (!str.eof()) {
			size_t name;
			str.read((char*)&name, sizeof(size_t));
			only_geometric.insert((IfcSchema::Type::Enum) name);
		}
	}

	std::set<IfcSchema::Type::Enum> property_types {
		IfcSchema::Type::IfcRelDefines, 
		IfcSchema::Type::IfcPropertySetDefinition, 
		IfcSchema::Type::IfcTypeObject, 
		IfcSchema::Type::IfcProperty, 
		IfcSchema::Type::IfcPhysicalQuantity,
		IfcSchema::Type::IfcRelAssociatesClassification,
		IfcSchema::Type::IfcRelAssociatesMaterial,
		IfcSchema::Type::IfcMaterialList,
		IfcSchema::Type::IfcMaterialLayerSetUsage,
		IfcSchema::Type::IfcMaterialLayerSet,
		IfcSchema::Type::IfcMaterialLayer,
		IfcSchema::Type::IfcMaterial
	};

	std::vector<IfcUtil::IfcBaseClass*> new_defs, old_defs, old_prop_defs, old_geom_defs, old_box_defs, all_old_defs, all_defs;

	std::for_each(only_geometric.begin(), only_geometric.end(), [&f, &old_geom_defs](IfcSchema::Type::Enum t) {
		auto insts = f.entitiesByType(t);
		std::for_each(insts->begin(), insts->end(), [t, &old_geom_defs](IfcUtil::IfcBaseClass* inst) {
			if (inst->declaration().type() == t) {
				old_geom_defs.push_back(inst);
			}
		});
	});

	std::for_each(f.begin(), f.end(), [&only_geometric, &old_defs, &old_prop_defs, &property_types](const auto& pair) {
		IfcUtil::IfcBaseClass* inst = pair.second;
		
		// This is checked the other way around to include subtypes
		bool is_property = false;
		for (auto pty : property_types) {
			if (inst->declaration().is(pty)) {
				is_property = true;
				break;
			}
		}
		
		auto ty = inst->declaration().type();

		if (is_property) {
			old_prop_defs.push_back(inst);
		} else if (only_geometric.find(ty) == only_geometric.end()) {
			old_defs.push_back(inst);
		}
	});
	
	IfcSchema::IfcRepresentationContext* context = 0;
	auto reps = (*f.entitiesByType<IfcSchema::IfcProductDefinitionShape>()->begin())->Representations();
	std::for_each(reps->begin(), reps->end(), [&context](auto rep) {
		IfcGeom::IfcRepresentationShapeItems items;
		if (rep->RepresentationIdentifier() == "Body") {
			context = rep->ContextOfItems();
		}
	});
	
	auto id = f.FreshId();
	int num_points_added = 0;

	{
		std::ifstream str(cache_fn.c_str(), std::ios_base::binary);
		while (!str.eof()) {
			size_t name;
			double xyz[6];

			str.read((char*)&name, sizeof(size_t));
			str.read((char*)xyz, sizeof(size_t));

			IfcSchema::IfcCartesianPoint* corner = new IfcSchema::IfcCartesianPoint(std::vector<double>{xyz[0], xyz[1], xyz[2]});;
			IfcSchema::IfcBoundingBox* bbox = new IfcSchema::IfcBoundingBox(corner, xyz[3] - xyz[0], xyz[4] - xyz[1], xyz[5] - xyz[2]);
			IfcSchema::IfcRepresentationItem::list::ptr items(new IfcSchema::IfcRepresentationItem::list);
			items->push(bbox);

			IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(context, std::string("Body"), std::string("BoundingBox"), items);
			IfcSchema::IfcRepresentation::list::ptr new_reps(new IfcSchema::IfcRepresentation::list);
			new_reps->push(rep);

			IfcSchema::IfcProductDefinitionShape* new_def = new IfcSchema::IfcProductDefinitionShape(boost::none, boost::none, new_reps);

			corner->data().isWritable()->setId(id++);

			// NB: Corner is added to existing definitions
			old_defs.push_back(corner); ++num_points_added;
			new_defs.push_back(bbox);
			new_defs.push_back(rep);
			new_defs.push_back(new_def);
		}
	}

	std::for_each(new_defs.begin(), new_defs.end(), [&id](auto new_def) {
		new_def->data().isWritable()->setId(id++);
	});

	auto iden = [](IfcUtil::IfcBaseClass* inst) { return inst; };

	std::set<IfcSchema::Type::Enum> old_new_geom_types;

	std::vector<std::vector<IfcUtil::IfcBaseClass*>*> all_vectors = std::vector<std::vector<IfcUtil::IfcBaseClass*>*>{ &new_defs, &old_prop_defs, &old_defs, &old_geom_defs };
	for (auto vec_ : all_vectors) {
		auto& vec = *vec_;
		for (auto& inst : vec) {
			old_new_geom_types.insert(inst->declaration().type());
		}
	}

	all_old_defs.insert(all_old_defs.end(), old_defs.begin(), old_defs.end());
	all_old_defs.insert(all_old_defs.end(), old_prop_defs.begin(), old_prop_defs.end());
	all_old_defs.insert(all_old_defs.end(), old_geom_defs.begin(), old_geom_defs.end());
	all_defs.insert(all_defs.end(), all_old_defs.begin(), all_old_defs.end());
	all_defs.insert(all_defs.end(), new_defs.begin(), new_defs.end());
	old_box_defs.insert(old_box_defs.end(), old_defs.begin(), old_defs.end());
	old_box_defs.insert(old_box_defs.end(), new_defs.begin(), new_defs.end());
	auto contexts = f.entitiesByType<IfcSchema::IfcRepresentationContext>();
	old_box_defs.insert(old_box_defs.end(), contexts->begin(), contexts->end());

	{
		int num_insts1 = std::distance(all_old_defs.begin(), all_old_defs.end());
		int num_insts2 = std::distance(f.begin(), f.end());
		if ((num_insts1 - num_points_added) != num_insts2) {
			std::cerr << "Missign instances " << num_insts1 << " - " << num_points_added << " != " << num_insts2 << std::endl;
			abort();
		}
	}

	multifile_instance_locator* locator = new multifile_instance_locator(
		old_new_geom_types.begin(), old_new_geom_types.end(),
		all_old_defs.begin(), all_old_defs.end());

	IfcParse::Hdf5Settings settings;
	settings.profile() = IfcParse::Hdf5Settings::padded;
	settings.compress() = true;
	settings.chunk_size() = 256;

	H5::H5File hdf(argv[1] + std::string(".hdf"), H5F_ACC_TRUNC);
	H5::H5File geom_hdf(argv[1] + std::string("-geometry.hdf"), H5F_ACC_TRUNC);
	H5::H5File box_hdf(argv[1] + std::string("-bounding-boxes.hdf"), H5F_ACC_TRUNC);
	H5::H5File prop_hdf(argv[1] + std::string("-properties.hdf"), H5F_ACC_TRUNC);

	hdf.createGroup("geometry").close();
	hdf.createGroup("bounding-boxes").close();
	hdf.createGroup("properties").close();

	hdf.mount("geometry", geom_hdf, H5::PropList::DEFAULT);
	hdf.mount("bounding-boxes", box_hdf, H5::PropList::DEFAULT);
	hdf.mount("properties", prop_hdf, H5::PropList::DEFAULT);

	H5::Group main_population = hdf.createGroup("population");
	H5::Group geom_population = hdf.createGroup("geometry/population");
	H5::Group box_population = hdf.createGroup("bounding-boxes/population");
	H5::Group prop_population = hdf.createGroup("properties/population");

	{
		IfcParse::IfcHdf5File ifc_hdf5(hdf, get_schema(), settings);
		IfcParse::instance_categorizer categorizer(all_defs.begin(), all_defs.end());
		ifc_hdf5.write_schema(&categorizer);

		{
			IfcParse::instance_enumerator enumerator(&f.header(), old_defs.begin(), old_defs.end());
			ifc_hdf5.write_population(main_population, enumerator, locator);
		}
		
		{
			IfcParse::instance_enumerator enumerator(&f.header(), old_geom_defs.begin(), old_geom_defs.end());
			ifc_hdf5.write_population(geom_population, enumerator, locator);
		}

		{
			IfcParse::instance_enumerator enumerator(&f.header(), old_prop_defs.begin(), old_prop_defs.end());
			ifc_hdf5.write_population(prop_population, enumerator, locator);
		}

		{
			// locator is setup with all_old_defs, need to switch to new_defs + old_defs for the cartesian points
			// NB: also geom rep context
			locator->next(box_population, old_box_defs.begin(), old_box_defs.end());

			IfcParse::instance_enumerator enumerator(&f.header(), new_defs.begin(), new_defs.end());
			ifc_hdf5.write_population(box_population, enumerator, locator);
		}
	}
}