/****************************************************************************
 * SVG fill									        					    *
 * 																			*
 * Copyright(C) 2020 AECgeeks and Bimforce								    *
 * 																		    *
 * This program is free software; you can redistribute it and/or		    *
 * modify it under the terms of the GNU Lesser General Public			    *
 * License as published by the Free Software Foundation; either			    *
 * version 3 of the License, or (at your option) any later version.		    *
 * 																		    *
 * This program is distributed in the hope that it will be useful,		    *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of		    *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU	    *
 * Lesser General Public License for more details.						    *
 * 																		    *
 * You should have received a copy of the GNU Lesser General Public License *
 * along with this program; if not, write to the Free Software Foundation,  *
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.	    *
 ****************************************************************************/

#ifndef SVGFILL_H
#define SVGFILL_H

#ifdef IFC_SHARED_BUILD
#ifdef _WIN32
#ifdef svgfill_EXPORTS
#define SVGFILL_API __declspec(dllexport)
#else
#define SVGFILL_API __declspec(dllimport)
#endif
#else // simply assume *nix + GCC-like compiler
#define SVGFILL_API __attribute__((visibility("default")))
#endif
#else
#define SVGFILL_API
#endif

#include <boost/optional.hpp>

#include <array>
#include <vector>

namespace svgfill {
	typedef std::array<double, 2> point_2;
	typedef std::array<point_2, 2> line_segment_2;
	typedef std::vector<point_2> loop_2;
	struct SVGFILL_API polygon_2 {
		loop_2 boundary;
		std::vector<loop_2> inner_boundaries;
		point_2 point_inside;
	};

	enum solver {
		CARTESIAN_DOUBLE,
		CARTESIAN_QUOTIENT,
		FILTERED_CARTESIAN_QUOTIENT,
		EXACT_PREDICATES,
		EXACT_CONSTRUCTIONS
	};

	class SVGFILL_API abstract_arrangement {
	public:
		virtual ~abstract_arrangement() {}
		virtual bool operator()(double eps, const std::vector<svgfill::line_segment_2>& segments, std::function<void(float)>& progress) = 0;
		virtual bool write(std::vector<svgfill::polygon_2>& polygons, std::function<void(float)>& progress) = 0;
		virtual void merge(const std::vector<int>& edge_indices) = 0;
		virtual std::vector<int> get_face_pairs() = 0;
		virtual size_t num_edges() = 0;
		virtual size_t num_faces() = 0;
	};

	class SVGFILL_API context {
	private:
		solver solver_;
		double eps_;
		std::vector<line_segment_2> segments_;
		std::function<void(float)> progress_;
		// std::vector<polygon_2> polygons_;
		abstract_arrangement* arr_;

	public:
		context(solver s, double eps)
			: solver_(s)
			, eps_(eps)
			, arr_(nullptr)
		{}

		context(solver s, double eps, std::function<void(float)>& progress)
			: solver_(s)
			, eps_(eps)
			, progress_(progress)
			, arr_(nullptr)
		{}

		void add(const std::vector<line_segment_2>& segments);
		bool build();
		std::vector<int> get_face_pairs() {
			return arr_->get_face_pairs();
		}
		void merge(const std::vector<int>& edge_indices);
		void write(std::vector<std::vector<polygon_2>>&);
		size_t num_edges() { return arr_->num_edges(); }
		size_t num_faces() { return arr_->num_faces(); }

		~context() {
			delete arr_;
		}
	};

	SVGFILL_API bool svg_to_line_segments(const std::string& data, const boost::optional<std::string>& class_name, std::vector<std::vector<line_segment_2>>& segments);
	SVGFILL_API bool line_segments_to_polygons(solver s, double eps, const std::vector<std::vector<line_segment_2>>& segments, std::vector<std::vector<polygon_2>>& polygons);
	SVGFILL_API bool line_segments_to_polygons(solver s, double eps, const std::vector<std::vector<line_segment_2>>& segments, std::vector<std::vector<polygon_2>>& polygons, std::function<void(float)>& progress);
	SVGFILL_API std::string polygons_to_svg(const std::vector<std::vector<polygon_2>>& polygons, bool random_color=false);
	SVGFILL_API std::string polygons_to_svg(const std::vector<polygon_2>& polygons, bool random_color = false);
	SVGFILL_API bool svg_to_polygons(const std::string& data, const boost::optional<std::string>& class_name, std::vector<polygon_2>& polygons);
	SVGFILL_API bool arrange_polygons(const std::vector<polygon_2>& polygons, std::vector<polygon_2>& arranged);
}

#endif
