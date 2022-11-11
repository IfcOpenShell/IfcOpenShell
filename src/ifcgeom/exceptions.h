#pragma once

#include <string>
#include <exception>

#include "schema_agnostic/ifc_geom_api.h"

namespace ifcopenshell {
	namespace geometry {

		class IFC_GEOM_API geometry_exception : public std::exception {
		protected:
			std::string message;
		public:
			geometry_exception(const std::string& m)
				: message(m) {}
			virtual ~geometry_exception() throw () {}
			virtual const char* what() const throw() {
				return message.c_str();
			}
		};

		class IFC_GEOM_API too_many_faces_exception : public geometry_exception {
		public:
			too_many_faces_exception()
				: geometry_exception("Too many faces for operation") {}
		};
	}
}
