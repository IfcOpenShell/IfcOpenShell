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

#ifndef HDF5SETTINGS_H
#define HDF5SETTINGS_H

#include <string>
#include <vector>

namespace IfcParse {
	
	struct Hdf5Settings {
	private:
		bool compress_, fix_cartesian_point_, fix_global_id_, instantiate_select_, instantiate_inverse_;
		unsigned int chunk_size_;
		std::vector<std::string> ref_attributes_;

	public:
		enum Profile {
			standard,
			padded,
			standard_referenced,
			padded_referenced
		};

		static Profile ProfileFromString(const std::string& s) {
			if (s == "standard") return standard;
			if (s == "padded") return padded;
			if (s == "standard-referenced") return standard_referenced;
			if (s == "padded-referenced") return padded_referenced;
			throw std::exception("Unrecognized profile");
		}

	private:
		Profile profile_;

	public:
		Hdf5Settings()
			: compress_(false)
			, fix_cartesian_point_(false)
			, fix_global_id_(false)
			, instantiate_select_(false)
			, instantiate_inverse_(false)
			, chunk_size_(false)
			, profile_(standard)
		{}

		bool compress() const { return compress_; }
		bool fix_cartesian_point() const { return fix_cartesian_point_; }
		bool fix_global_id() const { return fix_global_id_; }
		bool instantiate_select() const { return instantiate_select_; }
		bool instantiate_inverse() const { return instantiate_inverse_; }
		
		bool& compress() { return compress_; }
		bool& fix_cartesian_point() { return fix_cartesian_point_; }
		bool& fix_global_id() { return fix_global_id_; }
		bool& instantiate_select() { return instantiate_select_; }
		bool& instantiate_inverse() { return instantiate_inverse_; }
		
		unsigned int chunk_size() const { return chunk_size_; }
		unsigned int& chunk_size() { return chunk_size_; }

		Profile profile() const { return profile_; }
		Profile& profile() { return profile_; }
		
		const std::vector<std::string>& ref_attributes() const { return ref_attributes_; }
		std::vector<std::string>& ref_attributes() { return ref_attributes_; }
	};

}

#endif