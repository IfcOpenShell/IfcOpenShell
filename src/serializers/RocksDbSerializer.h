#ifdef WITH_ROCKSDB

#include "../serializers/serializers_api.h"
#include "../ifcgeom/Serializer.h"
#include "../ifcparse/IfcFile.h"

#include <rocksdb/db.h>

class SERIALIZERS_API RocksDbSerializer : public Serializer {
private:
	rocksdb::DB* db_;
	std::string rocksdb_filename_;
	IfcParse::IfcFile* file_;
	IfcParse::IfcFile* output_file_;

public:
	RocksDbSerializer(IfcParse::IfcFile* file, const std::string& rocksdb_filename);

	virtual ~RocksDbSerializer() {}

	bool ready() { return true; }
	void writeHeader() {}

	void finalize();
	void setFile(IfcParse::IfcFile*) { throw IfcParse::IfcException("Should be supplied on construction"); }
};

#endif