/********************************************************************************
*                                                                              *
* This file is part of IfcOpenShell.                                           *
*                                                                              *
* IfcOpenShell is free software: you can redistribute it and/or modify         *
* it under the terms of the Lesser GNU General Public License as published by  *
* the Free Software Foundation, either version 3.0 of the License, or          *
* (at your option) any later version.                                          *
*                                                                              *
* IfcOpenShell is distributed in the hope that it will be useful,              *
* but WITHOUT ANY WARRANTY; without even the implied warranty of               *
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
* Lesser GNU General Public License for more details.                          *
*                                                                              *
* You should have received a copy of the Lesser GNU General Public License     *
* along with this program. If not, see <http://www.gnu.org/licenses/>.         *
*                                                                              *
********************************************************************************/

#include "mapping.h"

#include "../../ifcparse/IfcLogger.h"

using namespace IfcUtil;
using namespace ifcopenshell::geometry;

#define mapping POSTFIX_SCHEMA(mapping)

taxonomy::item* mapping::map(const IfcBaseClass* l) {
#include "bind_convert_impl.i"
	Logger::Message(Logger::LOG_ERROR, "No operation defined for:", l);
	return nullptr;
}

namespace {
	// A RAII-based mechanism to cast the conversion results
	// from map() into the right type expected by the higher
	// level typology items. An exception is thrown if the
	// types do not match or the result was nullptr. A copy
	// will be assigned to the higher level topology member
	// and the original pointer will be deleted.

	// This class is also able to uplift some topology items
	// to higher level types, such as a loop to a face, which
	// is why the cast operator does not return a reference.
	template <typename T>
	class as {
	private:
		taxonomy::item* item_;

	public:
		as(taxonomy::item* item) : item_(item) {}
		operator T() const {
			if (!item_) {
				throw taxonomy::topology_error;
			}
			T* t = dynamic_cast<T*>(item_);
			if (t) {
				return *t;
			} else {
				if constexpr (std::is_same<T, topology::face>::value) {
					topology::loop* loop = dynamic_cast<T*>(item_);
					if (loop) {
						return topology::face(loop.id, loop.matrix, *loop);
					}
				}
				throw taxonomy::topology_error;
			}
		}
		~as() {
			delete item;
		}
	};
};

taxonomy::item* mapping::map(const IfcSchema::IfcExtrudedAreaSolid* inst) {
	return new taxonomy::extrusion(
		inst->data().id(),
		as<taxonomy::matrix4>(map(inst->Position())),
		as<taxonomy::face>(map(inst->SweptArea())),
		as<taxonomy::direction3>(map(inst->ExtrudedDirection())),
		inst->Depth()
	);
}
