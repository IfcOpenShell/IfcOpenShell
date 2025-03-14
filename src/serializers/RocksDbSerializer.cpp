#ifdef WITH_ROCKSDB

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
	output_file_ = new IfcParse::IfcFile(file_->schema(), IfcParse::FT_ROCKSDB, rocksdb_filename_);
}

void RocksDbSerializer::finalize()
{
	// Build a map of instances and their references/dependencies
	std::map<uint32_t, std::set<uint32_t>> dependencies;
	std::visit([&dependencies](const auto& m) {
		if constexpr (std::is_same_v<std::decay_t<decltype(m)>, IfcParse::impl::in_memory_file_storage>) {
			for (const auto& ps : m.byref_excl_) {
				for (const auto& p : ps.second) {
					dependencies[p].insert(std::get<0>(ps.first));
				}
			}
		}
	}, file_->storage_);
	// Add bottom-rank nodes, inv mapping does not contain them
	for (const auto& p : *file_) {
		dependencies[p.first];
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
		for (auto& p : dependencies) {
			for (auto& i : no_deps) {
				p.second.erase(i);
			}
		}
	}

	// Add them in topological order, so that add() never recurses into something not previously visited
	for (auto& i : deps_topo_order) {
		output_file_->addEntity(file_->instance_by_id(i), i);
	}

	// Copy inverses
	std::visit([this](const auto& m) {
		if constexpr (std::is_same_v<std::decay_t<decltype(m)>, IfcParse::impl::in_memory_file_storage>) {
			for (auto& p : m.byref_excl_) {
				std::get<IfcParse::impl::rocks_db_file_storage>(output_file_->storage_).byref_excl_.insert(p);
			}
		}
	}, file_->storage_);

	delete output_file_;
}

#endif