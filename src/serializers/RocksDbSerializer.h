#ifndef ROCKSDBSERIALIZER_H
#define ROCKSDBSERIALIZER_H
#ifdef IFOPSH_WITH_ROCKSDB

#include "../serializers/serializers_api.h"
#include "../ifcgeom/Serializer.h"
#include "../ifcparse/file.h"

#include <rocksdb/db.h>

class SERIALIZERS_API RocksDbSerializer : public Serializer {
private:
	rocksdb::DB* db_;
	std::string rocksdb_filename_;
	std::variant<ifcopenshell::file*, std::string> file_;
	ifcopenshell::file* output_file_;

	void write_streaming_();
public:
	RocksDbSerializer(ifcopenshell::file* file, const std::string& rocksdb_filename);
	RocksDbSerializer(const std::string& input_filename, const std::string& rocksdb_filename, bool stream);

	virtual ~RocksDbSerializer() {}

	bool ready() { return true; }
	void writeHeader() {}

	void finalize();
	void setFile(ifcopenshell::file*) { throw ifcopenshell::exception("Should be supplied on construction"); }
};

#endif
#endif