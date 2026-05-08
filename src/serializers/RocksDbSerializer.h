#ifndef ROCKSDBSERIALIZER_H
#define ROCKSDBSERIALIZER_H
#ifdef IFOPSH_WITH_ROCKSDB

#include "../serializers/serializers_api.h"
#include "../ifcgeom/Serializer.h"

#include <string>
#include <vector>

class SERIALIZERS_API RocksDbSerializer : public Serializer {
private:
	std::string input_filename_;
	std::string rocksdb_filename_;
	std::vector<std::string> skip_supertypes_;

	void write_streaming_();
public:
	RocksDbSerializer(const std::string& input_filename, const std::string& rocksdb_filename, const std::vector<std::string>& skip_supertypes = {});

	virtual ~RocksDbSerializer() {}

	bool ready() override { return true; }
	bool is_streaming() const override { return true; }
	void writeHeader() override {}

	void finalize() override;
	void setFile(ifcopenshell::file*) override { throw ifcopenshell::exception("Streaming serializer uses input filename supplied on construction"); }
};

#endif
#endif
