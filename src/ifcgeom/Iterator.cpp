#include "Iterator.h"

/**
* Initialize iterator's list of tasks.
*
* Will automatically process first element, if 'defer-processing-first-element' is not set to `true`.
*
* @return Returns true if the iterator is initialized with any elements, false otherwise.
*
* @note
* - A true return value does not guarantee successful initialization of all elements.
*   Some elements may have failed to initialize. Check had_error_processing_elements()
*   to see whether there were errors during the initialization.
*
* - For non-concurrent iterators, a false return may occur if initialization of the first
*   element fails, even if subsequent elements could be initialized successfully.
*/
bool IfcGeom::Iterator::initialize() {
	using std::chrono::high_resolution_clock;

	if (initialization_outcome_) {
		return *initialization_outcome_;
	}

	time_points[0] = high_resolution_clock::now();
	std::vector<ifcopenshell::geometry::geometry_conversion_task> reps;
	if (num_threads_ != 1) {
		// @todo this shouldn't be necessary with properly immutable taxonomy items
		converter_->mapping()->use_caching() = false;
	}
	try {
		converter_->mapping()->get_representations(reps, filters_);
	} catch (const std::exception& e) {
		Logger::Error(e);
	}
	time_points[1] = high_resolution_clock::now();

	for (auto& task : reps) {
		geometry_conversion_result res;
		res.index = task.index;
		if (!settings_.get<ifcopenshell::geometry::settings::NoParallelMapping>().get()) {
			res.representation = task.representation;
			res.products_2 = task.products;
		} else {
			res.item = converter_->mapping()->map(task.representation);
			if (!res.item) {
				continue;
			}
			std::transform(task.products->begin(), task.products->end(), std::back_inserter(res.products), [this, &res](IfcUtil::IfcBaseClass* prod) {
				auto prod_item = converter_->mapping()->map(prod);
				return std::make_pair(prod->as<IfcUtil::IfcBaseEntity>(), ifcopenshell::geometry::taxonomy::cast<ifcopenshell::geometry::taxonomy::geom_item>(prod_item)->matrix);
			});
		}
		tasks_.push_back(res);
	}

	if (settings_.get<ifcopenshell::geometry::settings::NoParallelMapping>().get() && settings_.get<ifcopenshell::geometry::settings::PermissiveShapeReuse>().get()) {
		std::unordered_map<
			ifcopenshell::geometry::taxonomy::item::ptr,
			std::vector<std::pair<IfcUtil::IfcBaseEntity*, ifcopenshell::geometry::taxonomy::matrix4::ptr>>> folded;

		for (auto& r : tasks_) {
			auto i = r.item;

			Eigen::Matrix4d m4 = Eigen::Matrix4d::Identity();

			while (auto col = std::dynamic_pointer_cast<ifcopenshell::geometry::taxonomy::collection>(i)) {
				if (col->children.size() == 1) {
					if (col->matrix) {
						m4 *= col->matrix->ccomponents();
					}
					i = col->children[0];
				} else {
					break;
				}
			}

			for (auto& p : r.products) {
				auto pl = ifcopenshell::geometry::taxonomy::matrix4::ptr(p.second->clone_());
				pl->components() *= m4;
				folded[i].push_back(
					{ p.first, pl }
				);
			}
		}

		if (folded.size() < tasks_.size()) {
			auto old_size = tasks_.size();
			tasks_.clear();
			size_t i = 0;
			for (auto& p : folded) {
				tasks_.emplace_back();
				tasks_.back().index = i++;
				tasks_.back().item = p.first;
				tasks_.back().products = p.second;
			}
			Logger::Notice("Merged " + std::to_string(old_size) + " tasks into " + std::to_string(tasks_.size()) + " tasks due to permissive shape reuse");
		}
	}

	if (settings_.get<ifcopenshell::geometry::settings::NoParallelMapping>().get()) {
		remove_offset_();
	}

	size_t num_products = 0;
	for (auto& r : tasks_) {
		num_products += !settings_.get<ifcopenshell::geometry::settings::NoParallelMapping>().get() ? r.products_2->size() : r.products.size();
	}

	time_points[2] = high_resolution_clock::now();

	/*
	// What to do, map representation and product individually?
	// There needs to be two options, mapped item respecting (does that still work?), and optimized based on topology sorting.
	// Or is the sorting not necessary if we just cache?

	std::vector<taxonomy::ptr> items;
	std::map<taxonomy::ptr, taxonomy::matrix4> placements;
	std::transform(products.begin(), products.end(), std::back_inserter(items), [this, &placements](IfcUtil::IfcBaseClass* p) {
	auto item = converter_->mapping()->map(p);
	// Product placements do not affect item reuse and should temporarily be swapped to identity
	if (item) {
	std::swap(placements[item], ((taxonomy::geom_ptr)item)->matrix);
	}
	return item;
	});
	items.erase(std::remove(items.begin(), items.end(), nullptr), items.end());
	std::sort(items.begin(), items.end(), taxonomy::less);
	auto it = items.begin();
	while (it < items.end()) {
	auto jt = std::upper_bound(it, items.end(), *it, taxonomy::less);
	geometry_conversion_result r;
	r.item = *it;
	std::transform(it, jt, std::back_inserter(r.products), [&r, &placements](taxonomy::ptr product_node) {
	return std::make_pair((IfcUtil::IfcBaseEntity*) product_node->instance, placements[product_node]);
	});
	tasks_.push_back(r);
	it = jt;
	}
	*/

	Logger::Notice("Created " + boost::lexical_cast<std::string>(tasks_.size()) + " tasks for " + boost::lexical_cast<std::string>(num_products) + " products");

	if (tasks_.size() == 0) {
		Logger::Warning("No representations encountered, aborting");
		initialization_outcome_.reset(false);
	} else if (!settings_.get<ifcopenshell::geometry::settings::DeferProcessingFirstElement>().get()) {

		task_iterator_ = tasks_.begin();

		done = 0;
		total = (int)tasks_.size();

		if (num_threads_ != 1) {
			init_future_ = std::async(std::launch::async, [this]() { process_concurrently(); });

			// wait for the first element, because after init(), get() can be called.
			// so the element conversion must succeed
			initialization_outcome_ = wait_for_element();
		} else {
			initialization_outcome_ = create();
		}
	} else {
		initialization_outcome_.reset(true);
	}

	return *initialization_outcome_;
}

void IfcGeom::Iterator::process_finished_rep(geometry_conversion_result* rep) {
	if (rep->elements.empty()) {
		return;
	}

	std::lock_guard<std::mutex> lk(element_ready_mutex_);

	all_processed_elements_.insert(all_processed_elements_.end(), rep->elements.begin(), rep->elements.end());
	all_processed_native_elements_.insert(all_processed_native_elements_.end(), rep->breps.begin(), rep->breps.end());

	if (!task_result_ptr_initialized) {
		task_result_iterator_ = all_processed_elements_.begin();
		native_task_result_iterator_ = all_processed_native_elements_.begin();
		task_result_ptr_initialized = true;
	}

	progress_ = (int)(++processed_ * 100 / tasks_.size());
}

void IfcGeom::Iterator::process_concurrently() {
	size_t conc_threads = num_threads_;
	if (conc_threads > tasks_.size()) {
		conc_threads = tasks_.size();
	}

	kernel_pool.reserve(conc_threads);
	for (unsigned i = 0; i < conc_threads; ++i) {
		kernel_pool.push_back(new ifcopenshell::geometry::Converter(std::unique_ptr<ifcopenshell::geometry::kernels::AbstractKernel>(converter_->kernel()->clone()), ifc_file, settings_));
	}

	std::vector<std::future<geometry_conversion_result*>> threadpool;

	for (auto& rep : tasks_) {
		ifcopenshell::geometry::Converter* K = nullptr;
		if (threadpool.size() < kernel_pool.size()) {
			K = kernel_pool[threadpool.size()];
		}

		while (threadpool.size() == conc_threads) {
			for (int i = 0; i < (int)threadpool.size(); i++) {
				auto& fu = threadpool[i];
				std::future_status status;
				status = fu.wait_for(std::chrono::seconds(0));
				if (status == std::future_status::ready) {
					process_finished_rep(fu.get());

					std::swap(threadpool[i], threadpool.back());
					threadpool.pop_back();
					std::swap(kernel_pool[i], kernel_pool.back());
					K = kernel_pool.back();
					break;
				} // if
			}   // for
		}	 // while

		std::future<geometry_conversion_result*> fu = std::async(
			std::launch::async, [this](
				ifcopenshell::geometry::Converter* kernel,
				ifcopenshell::geometry::Settings settings,
				geometry_conversion_result* rep) {
			// Catch exceptions to be safe from freezing the iterator.
			try {
				this->create_element_(kernel, settings, rep);
			} catch (const std::exception& e) {
				Logger::Error(
					std::string("Exception '") + e.what() +
					std::string("' occurred while iterator was creating a shape: "),
					rep->item->instance
				);
				had_error_processing_elements_ = true;
			} catch (...) {
				Logger::Error(
					"Unknown exception occurred while iteartor was creating a shape: ",
					rep->item->instance
				);
				had_error_processing_elements_ = true;
			}
			return rep;
		},
			K,
			std::ref(settings_),
			&rep);

		if (terminating_) {
			break;
		}

		threadpool.emplace_back(std::move(fu));
	}

	for (auto& fu : threadpool) {
		process_finished_rep(fu.get());
	}

	finished_ = true;

	Logger::SetProduct(boost::none);

	if (!terminating_) {
		Logger::Status("\rDone creating geometry (" + boost::lexical_cast<std::string>(all_processed_elements_.size()) +
			" objects)								");
	}
}

/// Computes model's bounding box (bounds_min and bounds_max).
/// @note Can take several minutes for large files.
void IfcGeom::Iterator::compute_bounds(bool with_geometry)
{
	for (int i = 0; i < 3; ++i) {
		bounds_min_.components()(i) = std::numeric_limits<double>::infinity();
		bounds_max_.components()(i) = -std::numeric_limits<double>::infinity();
	}

	if (with_geometry) {
		size_t num_created = 0;
		do {
			IfcGeom::Element* geom_object = get();
			const IfcGeom::TriangulationElement* o = static_cast<const IfcGeom::TriangulationElement*>(geom_object);
			const IfcGeom::Representation::Triangulation& mesh = o->geometry();
			auto mat = o->transformation().data()->ccomponents();
			Eigen::Vector4d vec, transformed;

			for (typename std::vector<double>::const_iterator it = mesh.verts().begin(); it != mesh.verts().end();) {
				const double& x = *(it++);
				const double& y = *(it++);
				const double& z = *(it++);
				vec << x, y, z, 1.;
				transformed = mat * vec;

				for (int i = 0; i < 3; ++i) {
					bounds_min_.components()(i) = std::min(bounds_min_.components()(i), transformed(i));
					bounds_max_.components()(i) = std::max(bounds_max_.components()(i), transformed(i));
				}
			}
		} while (++num_created, next());
	} else {
		std::vector<ifcopenshell::geometry::geometry_conversion_task> reps;
		converter_->mapping()->get_representations(reps, filters_);

		std::vector<IfcUtil::IfcBaseClass*> products;
		for (auto& r : reps) {
			std::copy(r.products->begin(), r.products->end(), std::back_inserter(products));
		}

		for (auto& product : products) {
			auto prod_item = converter_->mapping()->map(product);
			auto vec = ifcopenshell::geometry::taxonomy::cast<ifcopenshell::geometry::taxonomy::geom_item>(prod_item)->matrix->translation_part();

			for (int i = 0; i < 3; ++i) {
				bounds_min_.components()(i) = std::min(bounds_min_.components()(i), vec(i));
				bounds_max_.components()(i) = std::max(bounds_max_.components()(i), vec(i));
			}
		}
	}
}

const IfcUtil::IfcBaseClass* IfcGeom::Iterator::create_shape_model_for_next_entity() {
	geometry_conversion_result* task = nullptr;
	for (; task_iterator_ < tasks_.end();) {
		task = &*task_iterator_++;
		create_element_(converter_, settings_, task);
		if (task->elements.empty()) {
			task = nullptr;
		} else {
			break;
		}
	}
	if (task) {
		process_finished_rep(task);
		return task->item->instance->as<IfcUtil::IfcBaseClass>();
	} else {
		return nullptr;
	}
}

void IfcGeom::Iterator::create_element_(ifcopenshell::geometry::Converter* kernel, ifcopenshell::geometry::Settings settings, geometry_conversion_result* rep)
{
	if (!settings_.get<ifcopenshell::geometry::settings::NoParallelMapping>().get()) {
		rep->item = kernel->mapping()->map(rep->representation);
		if (!rep->item) {
			return;
		}
		std::transform(rep->products_2->begin(), rep->products_2->end(), std::back_inserter(rep->products), [this, &rep, kernel](IfcUtil::IfcBaseClass* prod) {
			auto prod_item = kernel->mapping()->map(prod);
			return std::make_pair(prod->as<IfcUtil::IfcBaseEntity>(), ifcopenshell::geometry::taxonomy::cast<ifcopenshell::geometry::taxonomy::geom_item>(prod_item)->matrix);
		});
	} else {
	}

	auto product_node = rep->products.front();
	const IfcUtil::IfcBaseEntity* product = product_node.first;
	const auto& place = product_node.second;

	Logger::SetProduct(product);

	IfcGeom::BRepElement* brep = static_cast<IfcGeom::BRepElement*>(decorate_with_cache_(GeometrySerializer::READ_BREP, (std::string)product->get("GlobalId"), std::to_string(rep->item->instance->as<IfcUtil::IfcBaseEntity>()->id()), [kernel, settings, product, place, rep]() {
		return kernel->create_brep_for_representation_and_product(rep->item, product, place);
	}));

	if (!brep) {
		return;
	}

	auto elem = process_based_on_settings(settings, brep);
	if (!elem) {
		return;
	}

	rep->breps = { brep };
	rep->elements = { elem };

	for (auto it = rep->products.begin() + 1; it != rep->products.end(); ++it) {
		const auto& p = *it;
		const IfcUtil::IfcBaseEntity* product2 = p.first;
		const auto& place2 = p.second;

		IfcGeom::BRepElement* brep2 = static_cast<IfcGeom::BRepElement*>(decorate_with_cache_(GeometrySerializer::READ_BREP, (std::string)product2->get("GlobalId"), std::to_string(rep->item->instance->as<IfcUtil::IfcBaseEntity>()->id()), [kernel, settings, product2, place2, brep]() {
			return kernel->create_brep_for_processed_representation(product2, place2, brep);
		}));
		if (brep2) {
			auto elem2 = process_based_on_settings(settings, brep2, dynamic_cast<IfcGeom::TriangulationElement*>(elem));
			if (elem2) {
				rep->breps.push_back(brep2);
				rep->elements.push_back(elem2);
			}
		}
	}
}

IfcGeom::Element* IfcGeom::Iterator::process_based_on_settings(ifcopenshell::geometry::Settings settings, IfcGeom::BRepElement* elem, IfcGeom::TriangulationElement* previous)
{
	if (settings.get<ifcopenshell::geometry::settings::IteratorOutput>().get() == ifcopenshell::geometry::settings::SERIALIZED) {
		try {
			return new IfcGeom::SerializedElement(*elem);
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Getting a serialized element from model failed.");
			return nullptr;
		}
	} else if (settings.get<ifcopenshell::geometry::settings::IteratorOutput>().get() == ifcopenshell::geometry::settings::TRIANGULATED) {
		// the part before the hyphen is the representation id
		auto gid2 = elem->geometry().id();
		auto hyphen = gid2.find("-");
		if (hyphen != std::string::npos) {
			gid2 = gid2.substr(0, hyphen);
		}

		return decorate_with_cache_(GeometrySerializer::READ_TRIANGULATION, elem->guid(), gid2, [elem, previous]() {
			try {
				if (!previous) {
					return new TriangulationElement(*elem);
				} else {
					return new TriangulationElement(*elem, previous->geometry_pointer());
				}
			} catch (...) {
				Logger::Message(Logger::LOG_ERROR, "Getting a triangulation element from model failed.");
			}
			return (TriangulationElement*)nullptr;
		});
	} else {
		return elem;
	}
}

bool IfcGeom::Iterator::wait_for_element() {
	while (true) {
		size_t s;
		{
			std::lock_guard<std::mutex> lk(element_ready_mutex_);
			s = all_processed_elements_.size();
		}
		if (s > async_elements_returned_) {
			++async_elements_returned_;
			return true;
		} else if (finished_) {
			return false;
		} else {
			std::this_thread::sleep_for(std::chrono::milliseconds(10));
		}
	}
}

void IfcGeom::Iterator::log_timepoints() const {
	using std::chrono::high_resolution_clock;
	using std::chrono::duration;
	using namespace std::string_literals;

	std::array<std::string, 3> labels = {
		"Initializing mapping"s,
		"Performing mapping"s,
		"Geometry interpretation"s
	};

	for (auto it = time_points.begin() + 1; it != time_points.end(); ++it) {
		auto jt = it - 1;
		duration<double, std::milli> ms_double = (*it) - (*jt);
		Logger::Notice(labels[std::distance(time_points.begin(), jt)] + " took " + std::to_string(ms_double.count()) + "ms");
	}
}

void IfcGeom::Iterator::validate_iterator_state() const {
	if (!initialization_outcome_) {
		throw std::runtime_error("Iterator not initialized");
	}

	// Causes:
	// - iterator was initialized but there were no elements to process
	// - iterator was initialized but 'defer-processing-first-element' setting is enabled
	// and some element should be processed manually first
	if (!task_result_ptr_initialized) {
		throw std::runtime_error("No elements processed");
	}

	if (task_result_ptr_exhausted) {
		throw std::runtime_error("Iterator is exhausted");
	}
}

/// Moves to the next shape representation, create its geometry, and returns the associated product.
/// Use get() to retrieve the created geometry.
const IfcUtil::IfcBaseClass* IfcGeom::Iterator::next() {
	using std::chrono::high_resolution_clock;
	validate_iterator_state();

	if (*native_task_result_iterator_ != *task_result_iterator_) {
		delete* native_task_result_iterator_;
	}
	delete* task_result_iterator_;

	if (num_threads_ != 1) {
		if (!wait_for_element()) {
			Logger::SetProduct(boost::none);
			time_points[3] = high_resolution_clock::now();
			log_timepoints();
			task_result_ptr_exhausted = true;
			return nullptr;
		}

		task_result_iterator_++;
		native_task_result_iterator_++;

		return (*task_result_iterator_)->product();
	} else {
		// Increment the iterator over the list of products using the current
		// shape representation
		if (task_result_iterator_ == --all_processed_elements_.end()) {
			if (!create()) {
				Logger::SetProduct(boost::none);
				time_points[3] = high_resolution_clock::now();
				log_timepoints();
				task_result_ptr_exhausted = true;
				return nullptr;
			}
		}

		task_result_iterator_++;
		native_task_result_iterator_++;

		return (*task_result_iterator_)->product();
	}
}

/// Gets the representation of the current geometrical entity.
IfcGeom::Element* IfcGeom::Iterator::get()
{
	validate_iterator_state();

	auto ret = *task_result_iterator_;

	// If we want to organize the element considering their hierarchy
	if (settings_.get<ifcopenshell::geometry::settings::UseElementHierarchy>().get()) {
		// We are going to build a vector with the element parents.
		// First, create the parent vector
		std::vector<const IfcGeom::Element*> parents;

		// if the element has a parent
		if (ret->parent_id() != -1) {
			const IfcGeom::Element* parent_object = NULL;
			bool hasParent = true;

			// get the parent
			try {
				parent_object = get_object(ret->parent_id());
			} catch (const std::exception& e) {
				Logger::Error(e);
				hasParent = false;
			}

			// Add the previously found parent to the vector
			if (hasParent) parents.insert(parents.begin(), parent_object);

			// We need to find all the parents
			while (parent_object != NULL && hasParent && parent_object->parent_id() != -1) {
				// Find the next parent
				try {
					parent_object = get_object(parent_object->parent_id());
				} catch (const std::exception& e) {
					Logger::Error(e);
					hasParent = false;
				}

				// Add the previously found parent to the vector
				if (hasParent) parents.insert(parents.begin(), parent_object);

				hasParent = hasParent && parent_object->parent_id() != -1;
			}

			// when done push the parent list in the Element object
			ret->SetParents(parents);
		}
	}

	return ret;
}

const IfcGeom::Element* IfcGeom::Iterator::get_object(int id) {
	ifcopenshell::geometry::taxonomy::matrix4::ptr m4;
	int parent_id = -1;
	std::string instance_type, product_name, product_guid;
	IfcUtil::IfcBaseEntity* ifc_product = 0;

	try {
		ifc_product = ifc_file->instance_by_id(id)->as<IfcUtil::IfcBaseEntity>();
		instance_type = ifc_product->declaration().name();

		if (ifc_product->declaration().is("IfcRoot")) {
			product_guid = (std::string)ifc_product->get("GlobalId");
			product_name = ifc_product->get_value<std::string>("Name", "");
		}

		auto parent_object = converter_->mapping()->get_decomposing_entity(ifc_product);
		if (parent_object) {
			parent_id = parent_object->id();
		}

		// fails in case of IfcProject
		auto mapped = converter_->mapping()->map(ifc_product);
		auto casted = mapped ? ifcopenshell::geometry::taxonomy::dcast<ifcopenshell::geometry::taxonomy::geom_item>(mapped) : nullptr;

		if (casted) {
			m4 = casted->matrix;
		}
	} catch (const std::exception& e) {
		Logger::Error(e);
	}
#ifdef IFOPSH_WITH_OPENCASCADE
	catch (const Standard_Failure& e) {
		if (e.GetMessageString() && strlen(e.GetMessageString())) {
			Logger::Error(e.GetMessageString());
		} else {
			Logger::Error("Unknown error returning product");
		}
	}
#endif
	catch (...) {
		Logger::Error("Unknown error returning product");
	}

	Element* ifc_object = new Element(settings_, id, parent_id, product_name, instance_type, product_guid, "", m4, ifc_product);
	return ifc_object;
}

const IfcUtil::IfcBaseClass* IfcGeom::Iterator::create() {
	const IfcUtil::IfcBaseClass* product = nullptr;
	try {
		product = create_shape_model_for_next_entity();
	} catch (const std::exception& e) {
		Logger::Error(e);
		had_error_processing_elements_ = true;
	}
#ifdef IFOPSH_WITH_OPENCASCADE
	catch (const Standard_Failure& e) {
		if (e.GetMessageString() && strlen(e.GetMessageString())) {
			Logger::Error(e.GetMessageString());
		} else {
			Logger::Error("Unknown error creating geometry");
		}
		had_error_processing_elements_ = true;
	}
#endif
	catch (...) {
		Logger::Error("Unknown error creating geometry");
		had_error_processing_elements_ = true;
	}
	return product;
}

ifcopenshell::geometry::taxonomy::direction3::ptr IfcGeom::Iterator::remove_offset_() {
	
	using namespace ifcopenshell::geometry::taxonomy;
	using namespace ifcopenshell::geometry::settings;
	
	if (!settings_.get<MaxOffset>().has()) {
		return nullptr;
	}
	
	if (!settings_.get<NoParallelMapping>().get()) {
		throw std::runtime_error("remove_offset() can only be called with defer-processing-first-element and no-parallel-mapping settings");
	}

	auto collect_offset = [&](const item::ptr& itm, const std::vector<std::pair<IfcUtil::IfcBaseEntity*, matrix4::ptr>>& pr) -> std::pair<double, Eigen::Vector3d> {
		std::function<std::pair<double, Eigen::Vector3d>(const item::ptr&, Eigen::Matrix4d)> traverse;
		traverse = [&](const item::ptr& node, Eigen::Matrix4d m4) -> std::pair<double, Eigen::Vector3d> {
			if (auto shl = std::dynamic_pointer_cast<shell>(node)) {
				auto p = shl->centroid();
				Eigen::Vector4d v;
				v << p->components()(0), p->components()(1), p->components()(2), 1.0;
				Eigen::Vector3d translation_part = (m4 * v).head<3>();
				double translation_amnt = translation_part.norm();
				if (translation_amnt > settings_.get<MaxOffset>().get()) {
					return { translation_amnt, translation_part };
				} else {
					return { 0.0, Eigen::Vector3d::Zero() };
				}
			} else {
				if (auto gi = std::dynamic_pointer_cast<geom_item>(node)) {
					if (gi->matrix) {
						m4 = m4 * gi->matrix->ccomponents();
					}
				}
				Eigen::Vector3d translation_part = m4.block<3, 1>(0, 3);
				double translation_amnt = translation_part.norm();
				if (translation_amnt > settings_.get<MaxOffset>().get()) {
					return { translation_amnt, translation_part };
				} else if (auto col = std::dynamic_pointer_cast<collection>(node)) {
					std::vector<std::pair<double, Eigen::Vector3d>> child_transforms;
					for (const auto& child : col->children) {
						child_transforms.push_back(traverse(child, m4));
					}
					if (!child_transforms.empty()) {
						return *std::max_element(child_transforms.begin(), child_transforms.end(),
							[](const auto& a, const auto& b) { return a.first < b.first; });
					}
				}
				return { 0.0, Eigen::Vector3d::Zero() };
			}
		};

		Eigen::Matrix4d m4 = Eigen::Matrix4d::Identity();
		if (pr.size() == 1 && pr[0].second) {
			m4 = pr[0].second->ccomponents();
		}
		return traverse(itm, m4);
	};

	Eigen::Vector3d vec;

	if (settings_.get<ApplyOffset>().has()) {
		auto vs = settings_.get<ApplyOffset>().get();
		if (vs.size() != 3) {
			throw std::runtime_error("ApplyOffset setting must be a vector of size 3");
		}
		vec = Eigen::Vector3d(vs[0], vs[1], vs[2]);
	} else {
		// Collect all norms and vectors
		std::vector<double> norms;
		std::vector<Eigen::Vector3d> vectors;
		for (const auto& task : tasks_) {
			auto result = collect_offset(task.item, task.products);
			norms.push_back(result.first);
			vectors.push_back(result.second);
		}

		// Find the median norm index
		std::vector<double> sorted_norms = norms;
		std::nth_element(sorted_norms.begin(), sorted_norms.begin() + sorted_norms.size() / 2, sorted_norms.end());
		double median = sorted_norms[sorted_norms.size() / 2];
		auto median_it = std::find(norms.begin(), norms.end(), median);
		size_t median_index = std::distance(norms.begin(), median_it);

		if (median_index >= vectors.size()) {
			return nullptr;
		}

		vec = -vectors[median_index];
	}

	Eigen::Matrix4d translation_matrix = Eigen::Matrix4d::Identity();
	translation_matrix.block<3, 1>(0, 3) = vec;

	auto remove_offset = [&](const item::ptr& itm, const std::vector<std::pair<IfcUtil::IfcBaseEntity*, matrix4::ptr>>& pr) -> bool {
		std::function<bool(const item::ptr&, Eigen::Matrix4d)> traverse;
		traverse = [&](const item::ptr& node, Eigen::Matrix4d m4) -> bool {
			if (auto shl = std::dynamic_pointer_cast<shell>(node)) {
				auto p = shl->centroid();
				Eigen::Vector4d v;
				v << p->components()(0), p->components()(1), p->components()(2), 1.0;
				Eigen::Vector3d translation_part = (m4 * v).head<3>();
				double translation_amnt = translation_part.norm();
				if (translation_amnt > settings_.get<MaxOffset>().get()) {
					shl->matrix = make<matrix4>(translation_matrix);
				}
				return true;
			} else {
				auto m4b = m4;
				if (auto gi = std::dynamic_pointer_cast<geom_item>(node)) {
					if (gi->matrix) {
						m4b = m4 * gi->matrix->ccomponents();
					}
					Eigen::Vector3d translation_part = m4b.block<3, 1>(0, 3);
					double translation_amnt = translation_part.norm();
					if (translation_amnt > settings_.get<MaxOffset>().get()) {
						auto inverted_rot_scale3 = m4.block<3, 3>(0, 0).inverse();
						Eigen::Matrix4d inverted_rot_scale = Eigen::Matrix4d::Identity();
						inverted_rot_scale.block<3, 3>(0, 0) = inverted_rot_scale3;
						if (!gi->matrix) {
							gi->matrix = make<matrix4>();
						}
						gi->matrix->components() = (inverted_rot_scale * translation_matrix) * gi->matrix->ccomponents();
						return true;
					}
				}
				bool b = true;
				if (auto col = std::dynamic_pointer_cast<collection>(node)) {
					for (const auto& child : col->children) {
						if (!traverse(child, m4b)) {
							b = false;
						}
					}
				}
				return b;
			}
		};

		Eigen::Matrix4d m4 = Eigen::Matrix4d::Identity();
		if (pr.size() == 1 && pr[0].second) {
			m4 = pr[0].second->ccomponents();
		}
		return traverse(itm, m4);
	};

	size_t num_offset_applied = 0;
	for (auto& task : tasks_) {
		bool all_applied = true;
		for (auto& p : task.products) {
			auto bb = p.second->components().block<3, 1>(0, 3);
			double translation_amnt = bb.norm();
			if (translation_amnt > settings_.get<MaxOffset>().get()) {
				// block has an underlying mutable ref to the matrix
				bb += vec;
			} else {
				all_applied = false;
			}
		}
		if (all_applied) {
			num_offset_applied += 1;
			continue;
		}
		if (remove_offset(task.item, task.products)) {
			num_offset_applied += 1;
		}
	}

	Logger::Notice("Removed large offsets within " + std::to_string(num_offset_applied) + " products");
	Logger::Notice("Offset applied (" + std::to_string(vec(0)) + "," + std::to_string(vec(1)) + "," + std::to_string(vec(2)) + ")");

	return make<direction3>(vec);
}

IfcGeom::Iterator::~Iterator() {
	if (num_threads_ != 1) {
		terminating_ = true;

		if (init_future_.valid()) {
			init_future_.wait();
		}
	}

	for (auto& k : kernel_pool) {
		delete k;
	}

	if (task_result_ptr_initialized) {
		while (task_result_iterator_ != --all_processed_elements_.end()) {
			if (*native_task_result_iterator_ != *task_result_iterator_) {
				delete* native_task_result_iterator_;
			}
			delete* task_result_iterator_++;
			native_task_result_iterator_++;
		}
	}

	delete converter_;
}
