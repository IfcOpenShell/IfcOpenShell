#ifndef ROCKSDBSERIALIZER_H
#define ROCKSDBSERIALIZER_H
#ifdef IFOPSH_WITH_ROCKSDB

#include "../serializers/serializers_api.h"
#include "../ifcgeom/Serializer.h"
#include "../ifcparse/IfcFile.h"

#include <rocksdb/db.h>

class SERIALIZERS_API RocksDbSerializer : public Serializer {
private:
	rocksdb::DB* db_;
	std::string rocksdb_filename_;
	std::variant<IfcParse::IfcFile*, std::string> file_;
	IfcParse::IfcFile* output_file_;

	void write_streaming_();
	void write_non_streaming_();
public:
	RocksDbSerializer(IfcParse::IfcFile* file, const std::string& rocksdb_filename);
	RocksDbSerializer(const std::string& input_filename, const std::string& rocksdb_filename, bool stream);

	virtual ~RocksDbSerializer() {}

	bool ready() { return true; }
	void writeHeader() {}

	void finalize();
	void setFile(IfcParse::IfcFile*) { throw IfcParse::IfcException("Should be supplied on construction"); }
};

#endif
#endif