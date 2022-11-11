#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::item* mapping::map_impl(const IfcSchema::IfcPolyLoop* inst) {
	taxonomy::loop* loop = new taxonomy::loop;
	
	taxonomy::point3 first, previous;
	bool is_first = true;
	
	auto points = inst->Polygon();
	for (auto& point : *points) {
		auto p = as<taxonomy::point3>(map(point));
		if (is_first) {
			previous = first = p;
			is_first = false;
		} else {
			auto edge = new taxonomy::edge;
			edge->start = previous;
			edge->end = p;
			loop->children.push_back(edge);
			previous = p;
		}
	}
	
	auto edge = new taxonomy::edge;
	edge->start = previous;
	edge->end = first;
	loop->children.push_back(edge);
	
	if (loop->children.size() < 3) {
		Logger::Warning("Not enough edges for", inst);
		delete loop;
		return nullptr;
	}
	return loop;
}