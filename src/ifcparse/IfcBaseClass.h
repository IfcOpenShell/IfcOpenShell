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

#include "../ifcparse/IfcEntityInstanceData.h"
#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/utils.h"

#include <boost/shared_ptr.hpp>

class Argument;
class IfcEntityList;

namespace IfcUtil {

	class IFC_PARSE_API IfcBaseClass {
    protected:
		IfcEntityInstanceData* data_;

		static bool is_null(const IfcBaseClass* not_this) {
			return !not_this;
		}
        
	public:
        IfcBaseClass() : data_(0) {}
		IfcBaseClass(IfcEntityInstanceData* d) : data_(d) {}
		virtual ~IfcBaseClass() { delete data_; }
        
        const IfcEntityInstanceData& data() const { return *data_; }
		IfcEntityInstanceData& data() { return *data_; }
        void data(IfcEntityInstanceData* d);
        
        virtual const IfcParse::declaration& declaration() const = 0;

		template <class T>
		T* as() {
			// @todo: do not allow this to be null in the first place
			if (is_null(this)) {
				return static_cast<T*>(0);
			}
			return declaration().is(T::Class())
				? static_cast<T*>(this)
				: static_cast<T*>(0);
		}

		template <class T>
		const T* as() const {
			if (is_null(this)) {
				return static_cast<const T*>(0);
			}
			return declaration().is(T::Class())
				? static_cast<const T*>(this)
				: static_cast<const T*>(0);
		}
	};

	class IFC_PARSE_API IfcLateBoundEntity : public IfcBaseClass {
	private:
		const IfcParse::declaration* decl_;

	public:
		IfcLateBoundEntity(const IfcParse::declaration* decl, IfcEntityInstanceData* data) : IfcBaseClass(data), decl_(decl) {}

		virtual const IfcParse::declaration& declaration() const {
			return *decl_;
		}
	};

	class IFC_PARSE_API IfcBaseEntity : public IfcBaseClass {
	public:
		IfcBaseEntity() : IfcBaseClass() {}
		IfcBaseEntity(IfcEntityInstanceData* d) : IfcBaseClass(d) {}

		virtual const IfcParse::entity& declaration() const = 0;

		Argument* get(const std::string& name) const;

		boost::shared_ptr<IfcEntityList> get_inverse(const std::string& a) const;
	};

	// TODO: Investigate whether these should be template classes instead
	class IFC_PARSE_API IfcBaseType : public IfcBaseClass {
	public:
		IfcBaseType() : IfcBaseClass() {}
		IfcBaseType(IfcEntityInstanceData* d) : IfcBaseClass(d) {}

		virtual const IfcParse::declaration& declaration() const = 0;
	};

}

#endif
