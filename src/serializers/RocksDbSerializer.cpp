#ifdef IFOPSH_WITH_ROCKSDB

#include "RocksDbSerializer.h"

#include <rocksdb/options.h>

#include "../ifcparse/IfcLogger.h"

RocksDbSerializer::RocksDbSerializer(IfcParse::IfcFile* file, const std::string& rocksdb_filename)
	: file_(file)
	, rocksdb_filename_(rocksdb_filename)
{
	/*rocksdb::Options options;
	options.create_if_missing = true;
	options.merge_operator.reset(new ConcatenateIdMergeOperator());
	rocksdb::Status status = rocksdb::DB::Open(options, rocksdb_filename, &db_);*/

	output_file_ = new IfcParse::IfcFile(file->schema(), IfcParse::FT_ROCKSDB, rocksdb_filename_);

	// We promise never to add the same instance twice
	output_file_->check_existance_before_adding = false;
	// We only copy one file into an empty container so units will match
	output_file_->calculate_unit_factors = false;
}

RocksDbSerializer::RocksDbSerializer(const std::string& input_filename, const std::string& rocksdb_filename, bool stream)
	: file_(input_filename)
	, rocksdb_filename_(rocksdb_filename)
{
}

namespace {
	// @nb copied from IfcEntityInstanceData.cpp but operating on unresolved instances
	bool serialize(std::string& val, const IfcParse::reference_or_simple_type& t)
	{
		auto s = sizeof(size_t);
		val.resize(s + 2);
		val[0] = TypeEncoder::encode_type<IfcUtil::IfcBaseClass*>();
		// 1 = entity - stored by id (entity name)
		// 2 = type - stored by identity (internal counter in class)
		val[1] = t.index() == 0 ? 'i' : 't';
		size_t iden;
		if (auto* name = std::get_if<IfcParse::InstanceReference>(&t)) {
			iden = *name;
		} else if (auto* inst = std::get_if<IfcUtil::IfcBaseClass*>(&t)) {
			iden = (*inst)->identity();
		}
		memcpy(val.data() + 2, &iden, s);
		return true;
	}

	bool serialize(std::string& val, const std::vector<IfcParse::reference_or_simple_type>& t)
	{
		// no attempt at alignment
		val.resize(t.size() * (sizeof(size_t) + 1) + 1);
		val[0] = TypeEncoder::encode_type<aggregate_of_instance::ptr>();
		char* ptr = val.data() + 1;
		for (auto it = t.begin(); it != t.end(); ++it) {
			*ptr = it->index() == 0 ? 'i' : 't';
			ptr++;
			size_t iden = 0;
			if (auto* name = std::get_if<IfcParse::InstanceReference>(&*it)) {
				iden = *name;
			} else if (auto* inst = std::get_if<IfcUtil::IfcBaseClass*>(&*it)) {
				iden = (*inst)->identity();
			}
			memcpy(ptr, &iden, sizeof(size_t));
			ptr += sizeof(size_t);
		}
		return true;
	}

	bool serialize(std::string& val, const std::vector<std::vector<IfcParse::reference_or_simple_type>>& t)
	{
		std::ostringstream oss;
		oss.put(TypeEncoder::encode_type<aggregate_of_aggregate_of_instance::ptr>());

		auto write_size = [&oss](size_t sz) {
			std::string size_str;
			size_str.resize(sizeof(size_t));
			memcpy(size_str.data(), &sz, sizeof(size_t));
			oss.write(size_str.data(), size_str.size());
		};

		// write_size(t.size());

		for (auto it = t.begin(); it != t.end(); ++it) {
			// size of inner aggregate
			write_size(it->size() * 9);

			// values
			for (auto jt = it->begin(); jt != it->end(); ++jt) {
				char c = jt->index() == 0 ? 'i' : 't';
				oss.put(c);
				size_t iden = 0;
				if (auto* name = std::get_if<IfcParse::InstanceReference>(&*jt)) {
					iden = *name;
				} else if (auto* inst = std::get_if<IfcUtil::IfcBaseClass*>(&*jt)) {
					iden = (*inst)->identity();
				}
				std::string iden_str;
				iden_str.resize(sizeof(size_t));
				memcpy(iden_str.data(), &iden, sizeof(size_t));
				oss.write(iden_str.data(), iden_str.size());
			}
		}

		val = oss.str();

		return true;
	}
}

namespace {
	template <typename T>
	std::string to_string_fixed_width(const T& t, size_t w) {
		// @todo currently inactive
		std::ostringstream oss;
		oss << /*std::setfill('0') << std::setw(w) <<*/ t;
		return oss.str();
	}
}

void RocksDbSerializer::write_streaming_() {
	const auto& input_filename = std::get<std::string>(file_);

	IfcParse::impl::rocks_db_file_storage storage(rocksdb_filename_, nullptr);

	std::string tmp;

	IfcParse::InstanceStreamer streamer(input_filename);

	// We do not want to coerce attribute counts here, because we want
	// to store exactly what is in the file for validation purposes
	streamer.coerce_attribute_count = false;

	while (streamer) {
		auto inst = streamer.read_instance();
		if (inst) {
			// name can be zero in case of header instances
			auto name = std::get<0>(*inst);
			const auto* decl = std::get<1>(*inst);
			const auto& data = std::get<2>(*inst);

			const bool is_header = decl->schema() == &Header_section_schema::get_schema();

			std::vector<IfcUtil::IfcBaseClass*> simple_type_instances;

			for (size_t i = 0; i < data.storage_->size(); i++) {
				auto val = data.get_attribute_value(nullptr, decl, 0, i);
				val.apply_visitor([&](const auto& t) {
					using T = std::decay_t<decltype(t)>;
					if constexpr (std::is_same_v<T, IfcUtil::IfcBaseClass*>) {
						// instance is per definition a simple type here, because instance
						// references are not resolved yet, but provided in vector of
						// references
						simple_type_instances.push_back(t);
					}
					rocks_db_attribute_storage{}.set(&storage, decl, name, i, t);
				});
			}

			std::set<size_t> type_identities_wrote_as_refs;

			for (auto& p : streamer.references()) {
				// @nb cast to int in order not be interpreted as a char when appending to string
				int index = p.first.index_;

				auto key = (is_header ? "h|" : (decl->as_entity() ? "i|" : "t|")) +
					(is_header ? decl->name() : std::to_string(p.first.name_)) + "|" +
					std::to_string(index);

				if (storage.db->Get(storage.ropts, key, &tmp) == rocksdb::Status::OK() && tmp.size() == (sizeof(size_t) + 2) && tmp[0] == TypeEncoder::encode_type<IfcUtil::IfcBaseClass*>() && tmp[1] == 't')
				{
					size_t iden;
					memcpy(&iden, tmp.data() + 2, sizeof(size_t));
					key = "t|" + std::to_string(iden) + "|0";
					type_identities_wrote_as_refs.insert(iden);
				}

				std::visit([&](const auto& v) {
					serialize(tmp, v);

					using T = std::decay_t<decltype(v)>;

					if constexpr (std::is_same_v<T, IfcParse::reference_or_simple_type>) {
						if (auto* inst = std::get_if<IfcUtil::IfcBaseClass*>(&v)) {
							// So this never happens?
							simple_type_instances.push_back(*inst);
						}
					} else if constexpr (std::is_same_v<T, std::vector<IfcParse::reference_or_simple_type>>) {
						for (auto const& inner : v) {
							if (auto* inst = std::get_if<IfcUtil::IfcBaseClass*>(&inner)) {
								simple_type_instances.push_back(*inst);
							}
						}
					} else if constexpr (std::is_same_v<T, std::vector<std::vector<IfcParse::reference_or_simple_type>>>) {
						for (auto const& inner : v) {
							for (auto const& innermost : inner) {
								if (auto* inst = std::get_if<IfcUtil::IfcBaseClass*>(&innermost)) {
									simple_type_instances.push_back(*inst);
								}
							}
						}
					}
				}, p.second);

				storage.db->Put(
					storage.wopts,
					key, tmp);

				auto write_inverse = [&](const IfcParse::reference_or_simple_type& v) {
					if (auto* ref = std::get_if<IfcParse::InstanceReference>(&v)) {
						auto key = "v|" + to_string_fixed_width(*ref, 10) + "|" + to_string_fixed_width(decl->index_in_schema(), 4) + "|" + to_string_fixed_width(index, 2);
						static std::string s;
						uint32_t vv = name;
						s.resize(sizeof(uint32_t));
						memcpy(s.data(), &vv, sizeof(uint32_t));
						storage.db->Merge(
							storage.wopts, key, s);
					}
				};

				std::visit([&](auto const& val) {
					using T = std::decay_t<decltype(val)>;

					if constexpr (std::is_same_v<T, IfcParse::reference_or_simple_type>) {
						write_inverse(val);
					} else if constexpr (std::is_same_v<T, std::vector<IfcParse::reference_or_simple_type>>) {
						std::for_each(val.begin(), val.end(), write_inverse);
					} else if constexpr (std::is_same_v<T, std::vector<std::vector<IfcParse::reference_or_simple_type>>>) {
						for (auto const& inner : val) {
							std::for_each(inner.begin(), inner.end(), write_inverse);
						}
					}
				}, p.second);
			}

			for (const auto* inst : simple_type_instances) {
				std::string s(sizeof(size_t), ' ');
				size_t v = inst->declaration().index_in_schema();
				memcpy(s.data(), &v, sizeof(size_t));

				storage.db->Put(
					storage.wopts,
					(inst->declaration().as_entity() ? "i|" : "t|") + std::to_string(inst->identity()) + "|_", s);

				if (type_identities_wrote_as_refs.find(inst->identity()) != type_identities_wrote_as_refs.end()) {
					// already written as reference, skip
					// only applies to the value though, the type declaration still needs to be written
					continue;
				}

				auto val = inst->get_attribute_value(0);
				if (val.array_.storage_ptr->size() > 0) {
					val.apply_visitor([&](const auto& t) {
						rocks_db_attribute_storage{}.set(&storage, &inst->declaration(), inst->identity(), 0, t);
					});
				}

				// @nb we also need to delete them
				// not anymore, as they are now registered as unique_ptr in the in_memory_file_storage
				// delete inst;
			}

			// Entity type as numeric ref to index_in_schema
			if (!is_header) {
				std::string s(sizeof(size_t), ' ');
				size_t v = decl->index_in_schema();
				memcpy(s.data(), &v, sizeof(size_t));
				storage.db->Put(
					storage.wopts,
					(decl->as_entity() ? "i|" : "t|") + std::to_string(name) + "|_", s);

				{
					size_t v = name;
					std::string s(sizeof(size_t), ' ');
					memcpy(s.data(), &v, sizeof(size_t));
					storage.db->Merge(storage.wopts, "t|" + std::to_string(decl->index_in_schema()), s);
				}
			}

			streamer.references().clear();
			streamer.inverses().clear();
		}
	}
}


void RocksDbSerializer::write_non_streaming_() {
	// Build a map of instances and their references/dependencies
	std::map<uint32_t, std::set<uint32_t>> dependencies, dependencies_inv;
	std::visit([&dependencies](const auto& m) {
		if constexpr (std::is_same_v<std::decay_t<decltype(m)>, IfcParse::impl::in_memory_file_storage>) {
			for (const auto& ps : m.byref_excl_) {
				for (const auto& p : ps.second) {
					dependencies[p].insert(std::get<0>(ps.first));
				}
			}
		}
	}, std::get<IfcParse::IfcFile*>(file_)->storage_);
	// Add bottom-rank nodes, inv mapping does not contain them
	for (const auto& p : *std::get<IfcParse::IfcFile*>(file_)) {
		dependencies[p.first];
	}

	for (auto& ps : dependencies) {
		for (auto& p : ps.second) {
			dependencies_inv[p].insert(ps.first);
		}
	}

	// Do a topological sort over the nodes
	std::vector<uint32_t> deps_topo_order;
	while (dependencies.size() > 0) {
		std::vector<uint32_t> no_deps;
		for (auto& ps : dependencies) {
			if (ps.second.size() == 0) {
				no_deps.push_back(ps.first);
			}
		}

		if (no_deps.size() == 0) {
			throw std::runtime_error("cyclic dependencies in model, unable to serialize");
		}

		for (auto& i : no_deps) {
			deps_topo_order.push_back(i);
		}

		// mutate mapping
		for (auto& i : no_deps) {
			dependencies.erase(i);
		}
		for (auto& i : no_deps) {
			for (auto& j : dependencies_inv[i]) {
				auto it = dependencies.find(j);
				if (it != dependencies.end()) {
					it->second.erase(i);
				}
			}
		}
	}

	// Add them in topological order, so that add() never recurses into something not previously visited
	for (auto& i : deps_topo_order) {
		output_file_->addEntity(std::get<IfcParse::IfcFile*>(file_)->instance_by_id(i), i);
	}

	// Copy inverses
	/* 
	// These are now back to being added in addEntity() / set_attribute_value()
	std::visit([this](const auto& m) {
		if constexpr (std::is_same_v<std::decay_t<decltype(m)>, IfcParse::impl::in_memory_file_storage>) {
			for (auto& p : m.byref_excl_) {
				// This is much slower than need be, because:
				//  - insert() first checks for existance [we know it does not] because insert() should not overwrite
				//  - insert() returns an pair<iterator, bool> [which is not used] which requires an expensive seek after the put.
				// This is left as-is for now, because anyway we want to build a streaming converter
				std::get<IfcParse::impl::rocks_db_file_storage>(output_file_->storage_).byref_excl_.insert(p);
			}
		}
	}, file_->storage_);
	*/

	delete output_file_;
}

void RocksDbSerializer::finalize() {
	if (file_.index() == 0) {
		write_non_streaming_();
	} else {
		write_streaming_();
	}
}


#endif