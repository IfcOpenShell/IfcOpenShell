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

#ifndef IFCBASECLASS_H
#define IFCBASECLASS_H

#include "ifc_parse_api.h"

#ifdef USE_IFC4
#include "../ifcparse/Ifc4enum.h"
#else
#include "../ifcparse/Ifc2x3enum.h"
#endif

#include "../ifcparse/IfcEntityInstanceData.h"

class Argument;

namespace IfcParse { // these have to be declared first in order for the virtual function below to be covariant. separate into different header file
	class declaration;
	class entity;
	class type_declaration;
}

namespace IfcUtil {

	class IFC_PARSE_API IfcBaseClass {
    protected:
		IfcAbstractEntity* data_;
        
	public:
        IfcBaseClass() : data_(0) {}
		IfcBaseClass(IfcAbstractEntity* d) : data_(d) {}
        virtual ~IfcBaseClass() {}
        
        const IfcAbstractEntity& data() const { return *data_; }
		IfcAbstractEntity& data() { return *data_; }
        void data(IfcAbstractEntity* d);
        
        virtual const IfcParse::declaration& declaration() const = 0;

		template <class T>
		T* as() {
			return is(T::Class())
				? static_cast<T*>(this)
				: static_cast<T*>(0);
		}

		template <class T>
		const T* as() const {
			return is(T::Class())
				? static_cast<const T*>(this)
				: static_cast<const T*>(0);
		}
	};

	class IFC_PARSE_API IfcBaseEntity : public IfcBaseClass {
	public:
		IfcBaseEntity() : IfcBaseClass() {}
		IfcBaseEntity(IfcAbstractEntity* d) : IfcBaseClass(d) {}

		virtual const IfcParse::entity& declaration() const = 0;
	};

	// TODO: Investigate whether these should be template classes instead
	class IFC_PARSE_API IfcBaseType : public IfcBaseEntity {
	public:
		IfcBaseType() : IfcBaseClass() {}
		IfcBaseType(IfcAbstractEntity* d) : IfcBaseClass(d) {}

		virtual const IfcParse::type_declaration& declaration() const = 0;
	};

}

#endif
