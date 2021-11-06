#include "mapping_undefine.i"
#define CLASS(T,V) \
	std::map<int,V> T;
#include "mapping_define_missing.i"

#include "mapping.i"