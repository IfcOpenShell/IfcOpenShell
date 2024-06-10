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

/********************************************************************************
 *                                                                              *
 * This examples exposes the IfcOpenShell API through a command-based stdin     *
 * interface                                                                    *
 *                                                                              *
 ********************************************************************************/

#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>

#include <iostream>
#include <boost/cstdint.hpp>

// NB: Streams are only re-opened as binary when compiled with MSVC currently.
//     It is unclear what the correct behaviour would be compiled with e.g MinGW
#if defined(_MSC_VER)
#define SET_BINARY_STREAMS
#endif

#ifdef SET_BINARY_STREAMS
#include <io.h>
#include <fcntl.h>
#endif

#include "../ifcgeom/Iterator.h"
#include "../ifcgeom/IfcGeomElement.h"
#include "../ifcparse/IfcFile.h"
#include "../ifcparse/IfcLogger.h"

#include "../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"

#if USE_VLD
#include <vld.h>
#endif

#include <GProp_GProps.hxx>
#include <BRepGProp.hxx>
#include <BRepBndLib.hxx>
#include <Bnd_Box.hxx>
#include <Geom_Plane.hxx>

#include <memory>

template <typename T>
union data_field {
    char buffer[sizeof(T)];
    T value;
};

template <typename T>
T sread(std::istream& s) {
    data_field<T> data;
    s.read(data.buffer, sizeof(T));
    return data.value;
}

template <>
std::string sread(std::istream& s) {
	int32_t len = sread<int32_t>(s);
	char* buf = new char[len + 1];
	s.read(buf, len);
	buf[len] = 0;
	while (len++ % 4) s.get();
	std::string str(buf);
	delete[] buf;
	return str;
}

template <typename T>
std::string format_json(const T& t) {
	return boost::lexical_cast<std::string>(t);
}

template <>
std::string format_json(const std::string& s) {
	// NB: No escaping whatsoever. Only use alphanumeric values.
	return "\"" + s + "\"";
}

template <>
std::string format_json(const double& d) {
	std::stringstream ss;
	ss << std::setprecision(std::numeric_limits<double>::digits10) << d;
	return ss.str();
}

template <>
std::string format_json(const gp_Dir& d) {
	std::stringstream ss;
	ss << std::setprecision(std::numeric_limits<double>::digits10) 
		<< "[" << d.X() << "," << d.Y() << "," << d.Z() << "]";
	return ss.str();
}

static std::streambuf *stdout_orig, *stdout_redir;

template <typename T>
void swrite(std::ostream& s, T t) {
	char buf[sizeof(T)];
	memcpy(buf, &t, sizeof(T));
	s.write(buf, sizeof(T));
}

template <>
void swrite(std::ostream& s, std::string t) {
	int32_t len = (int32_t)t.size();
	swrite(s, len);
	s.write(t.c_str(), len);
	while (len++ % 4) s.put(0);
}

template <typename T, typename U>
void swrite_array(std::ostream& s, const std::vector<U>& us) {
	if (std::is_same<T, U>::value) {
		swrite(s, std::string((char*)us.data(), us.size() * sizeof(U)));
	} else {
		std::vector<T> ts;
		ts.reserve(us.size());
		for (auto& u : us) {
			ts.push_back((T)u);
		}
		swrite_array<T, T>(s, ts);
	}
}

class Command {
protected:
	virtual void read_content(std::istream& s) = 0;
	virtual void write_content(std::ostream& s) = 0;
	int32_t iden;
	int32_t len;
public:
	void read(std::istream& s) {
		len = sread<int32_t>(s);
		read_content(s);
	}

	void write(std::ostream& s) {
		std::cout.rdbuf(stdout_orig);
		swrite(s, iden);
		std::ostringstream oss;
		write_content(oss);
		swrite(s, oss.str());
		s.flush();
		std::cout.rdbuf(stdout_redir);
	}

	Command(int32_t iden) : iden(iden) {}
};

const int32_t HELLO     = 0xff00;
const int32_t IFC_MODEL = HELLO     + 1;
const int32_t GET       = IFC_MODEL + 1;
const int32_t ENTITY    = GET       + 1;
const int32_t MORE      = ENTITY    + 1;
const int32_t NEXT      = MORE      + 1;
const int32_t BYE       = NEXT      + 1;
const int32_t GET_LOG   = BYE       + 1;
const int32_t LOG       = GET_LOG   + 1;
const int32_t DEFLECTION = LOG        + 1;
const int32_t SETTING    = DEFLECTION + 1;

class Hello : public Command {
private:
	std::string str;
protected:
	void read_content(std::istream& s) {
		str = sread<std::string>(s);
	}
	void write_content(std::ostream& s) {
		swrite(s, str);
	}
public:
	const std::string& string() { return str; }
	Hello() : Command(HELLO), str("IfcOpenShell-" IFCOPENSHELL_VERSION "-0") {}
};

class More : public Command {
private:
	bool more;
protected:
	void read_content(std::istream& s) {
		more = sread<int32_t>(s) == 1;
	}
	void write_content(std::ostream& s) {
		swrite<int32_t>(s, more ? 1 : 0);
	}
public:
	More(bool more) : Command(MORE), more(more) {}
};

class IfcModel : public Command {
private:
	std::string str;
protected:
	void read_content(std::istream& s) {
		str = sread<std::string>(s);
	}
	void write_content(std::ostream& s) {
		swrite(s, str);
	}
public:
	const std::string& string() { return str; }
	IfcModel() : Command(IFC_MODEL) {};
};

class Get : public Command {
protected:
	void read_content(std::istream& /*s*/) {}
	void write_content(std::ostream& /*s*/) {}
public:
	Get() : Command(GET) {};
};

class GetLog : public Command {
protected:
	void read_content(std::istream& /*s*/) {}
	void write_content(std::ostream& /*s*/) {}
public:
	GetLog() : Command(GET_LOG) {};
};

class WriteLog : public Command {
private:
	std::string str;
protected:
	void read_content(std::istream& s) {
		str = sread<std::string>(s);
	}
	void write_content(std::ostream& s) {
		swrite(s, str);
	}
public:
	WriteLog(const std::string& str) : Command(LOG), str(str) {};
};

class EntityExtension {
protected:
	bool trailing_, opened_;
	std::stringstream json_;

	template <typename T>
	void put_json(const std::string& k, T v) {
		if (!opened_) {
			json_ << "{";
			opened_ = true;
		}
		if (trailing_) {
			json_ << ",";
		}
		json_ << format_json(k) << ":" << format_json(v);
		trailing_ = true;
	}
public:
	EntityExtension()
		: trailing_(false)
		, opened_(false)
	{}

	void write_contents(std::ostream& s) {
		if (opened_) {
			json_ << "}";
		}

		// We do a 4-byte manual alignment
		std::string payload = json_.str();
		s << payload;
		if (payload.size() % 4) {
			s << std::string(4 - (payload.size() % 4), ' ');
		}
	}
};

class Entity : public Command {
private:
	const IfcGeom::TriangulationElement* geom;
	bool append_line_data;
	EntityExtension* eext_;
protected:
	void read_content(std::istream& /*s*/) {}
	void write_content(std::ostream& s) {
		swrite<int32_t>(s, geom->id());
		swrite(s, geom->guid());
		swrite(s, geom->name());
		swrite(s, geom->type());
		swrite<int32_t>(s, geom->parent_id());
		const auto& m = geom->transformation().data()->ccomponents();
		const double matrix_array[16] = {
			m(0,0), m(0,1), m(0,2), m(0,3),
			m(1,0), m(1,1), m(1,2), m(1,3),
			m(2,0), m(2,1), m(2,2), m(2,3),
			m(3,0),	m(3,1),	m(3,2),	m(3,3)
		};
		swrite(s, std::string((char*)matrix_array, 16 * sizeof(double)));
		
		// The first bit of the string is always the instance name of the representation.
		const std::string& representation_id = geom->geometry().id();
		const int integer_representation_id = atoi(representation_id.c_str());
		swrite<int32_t>(s, (int32_t)integer_representation_id);

		swrite_array<double>(s, geom->geometry().verts());
		swrite_array<float>(s, geom->geometry().normals());

		{
			std::vector<int32_t> indices;
			const std::vector<int>& faces = geom->geometry().faces();
			indices.reserve(faces.size());
			for (std::vector<int>::const_iterator it = faces.begin(); it != faces.end(); ++it) {
				indices.push_back(*it);
			} 
			swrite_array<int32_t>(s, indices);

			if (append_line_data) {
				std::vector<int32_t> lines;
				std::set<int32_t> faces_set (indices.begin(), indices.end());
				
				const std::vector<int>& edges = geom->geometry().edges();
				for ( std::vector<int>::const_iterator it = edges.begin(); it != edges.end(); ) {
					const int32_t i1 = *(it++);
					const int32_t i2 = *(it++);

					if (faces_set.find(i1) != faces_set.end() || faces_set.find(i2) != faces_set.end()) {
						continue;
					}

					lines.push_back(i1);
					lines.push_back(i2);
				}

				swrite_array<int32_t>(s, lines);
			}
		}
		{ 
			// We remove the blanks here from the material array. I.e. materials without a diffuse color
			std::vector<boost::optional<std::array<float, 4> > > diffuse_color_array;
			for (auto it = geom->geometry().materials().begin(); it != geom->geometry().materials().end(); ++it) {
				const auto& mat = **it;
				if (mat.diffuse) {
					const auto& color = mat.diffuse.ccomponents();
					diffuse_color_array.push_back(std::array<float, 4>{
						static_cast<float>(color(0)),
						static_cast<float>(color(1)),
						static_cast<float>(color(2)),
						mat.transparency == mat.transparency ? static_cast<float>(1. - mat.transparency) : 1.f
					});
				} else {
					diffuse_color_array.emplace_back();
				}
			}

			std::map<int, int> orig_to_condensed_index_map;
			std::vector<float> diffuse_color_array_condensed;
			
			int new_index = 0;
			for (size_t orig = 0; orig < diffuse_color_array.size(); ++orig) {
				auto& m = diffuse_color_array[orig];
				if (m) {
					for (int i = 0; i < 4; ++i) {
						diffuse_color_array_condensed.push_back((*m)[i]);
					}
					orig_to_condensed_index_map[orig] = new_index++;
				}
			}

			swrite(s, std::string((char*) diffuse_color_array_condensed.data(), diffuse_color_array_condensed.size() * sizeof(float)));

			std::vector<int32_t> material_indices;
			for (std::vector<int>::const_iterator it = geom->geometry().material_ids().begin(); it != geom->geometry().material_ids().end(); ++it) {
				// @todo use something like std::equal_range() ?
				auto jt = orig_to_condensed_index_map.find(*it);
				if (jt == orig_to_condensed_index_map.end()) {
					material_indices.push_back(-1);
				} else {
					material_indices.push_back(jt->second);
				}
			}

			swrite(s, std::string((char*) material_indices.data(), material_indices.size() * sizeof(int32_t)));
		}
		if (eext_) {
			eext_->write_contents(s);
		}
	}
public:
	Entity(const IfcGeom::TriangulationElement* geom, EntityExtension* eext = 0) : Command(ENTITY), geom(geom), append_line_data(false), eext_(eext) {};
};

class Next : public Command {
protected:
	void read_content(std::istream& /*s*/) {}
	void write_content(std::ostream& /*s*/) {}
public:
	Next() : Command(NEXT) {};
};

class Bye : public Command {
protected:
	void read_content(std::istream& /*s*/) {}
	void write_content(std::ostream& /*s*/) {}
public:
	Bye() : Command(BYE) {};
};

class Deflection : public Command {
private:
	double deflection_;
protected:
	void read_content(std::istream& s) {
		deflection_ = sread<double>(s);
	}
	void write_content(std::ostream& s) {
		swrite(s, deflection_);
	}
public:
	Deflection(double d = 0.) : Command(DEFLECTION), deflection_(d) {};
	double deflection() const { return deflection_; }
};

class Setting : public Command {
private:
	uint32_t id_;
	uint32_t value_;
protected:
	void read_content(std::istream& s) {
		id_ = sread<uint32_t>(s);
		value_ = sread<uint32_t>(s);
	}
	void write_content(std::ostream& s) {
		swrite(s, id_);
		swrite(s, value_);
	}
public:
	Setting(uint32_t k = 0, uint32_t v = 0) : Command(SETTING), id_(k), value_(v) {};
	uint32_t id() const { return id_; }
	uint32_t value() const { return value_; }
};

static const std::string TOTAL_SURFACE_AREA = "TOTAL_SURFACE_AREA";
static const std::string TOTAL_SHAPE_VOLUME = "TOTAL_SHAPE_VOLUME";
static const std::string SURFACE_AREA_ALONG_X = "SURFACE_AREA_ALONG_X";
static const std::string SURFACE_AREA_ALONG_Y = "SURFACE_AREA_ALONG_Y";
static const std::string SURFACE_AREA_ALONG_Z = "SURFACE_AREA_ALONG_Z";
static const std::string WALKABLE_SURFACE_AREA = "WALKABLE_SURFACE_AREA";
static const std::string LARGEST_FACE_AREA = "LARGEST_FACE_AREA";
static const std::string LARGEST_FACE_DIRECTION = "LARGEST_FACE_DIRECTION";
static const std::string BOUNDING_BOX_SIZE_ALONG_ = "BOUNDING_BOX_SIZE_ALONG_";
static const std::array<std::string, 3> XYZ = { "X", "Y", "Z" };

class QuantityWriter_v0 : public EntityExtension {
private:
	const IfcGeom::BRepElement* elem_;
public:
	QuantityWriter_v0(const IfcGeom::BRepElement* elem) :
		elem_(elem) 
	{
		put_json(TOTAL_SURFACE_AREA, 0.);
		put_json(TOTAL_SHAPE_VOLUME, 0.);
		if (elem_->type() == "IfcSpace") {
			put_json(WALKABLE_SURFACE_AREA, 0.);
		}	
	}
};

class QuantityWriter_v1 : public EntityExtension {
private:
	const IfcGeom::BRepElement* elem_;
public:
	QuantityWriter_v1(const IfcGeom::BRepElement* elem) :
		elem_(elem) {
		double a, b, c, largest_face_area = 0.;

		if (elem_->geometry().calculate_surface_area(a)) {
			put_json(TOTAL_SURFACE_AREA, a);
		}

		if (elem_->geometry().calculate_volume(a)) {
			put_json(TOTAL_SHAPE_VOLUME, a);
		}

		if (elem_->calculate_projected_surface_area(a, b, c)) {
			put_json(SURFACE_AREA_ALONG_X, a);
			put_json(SURFACE_AREA_ALONG_Y, b);
			put_json(SURFACE_AREA_ALONG_Z, c);
		}

		boost::optional<gp_Dir> largest_face_dir;

		{
			auto shp = elem_->geometry().as_compound(true);
			auto compound = ((ifcopenshell::geometry::OpenCascadeShape*)shp)->shape();
			delete shp;
			TopExp_Explorer exp(compound, TopAbs_FACE);
			for (; exp.More(); exp.Next()) {
				GProp_GProps prop;
				BRepGProp::SurfaceProperties(exp.Current(), prop);
				const double area = prop.Mass();
				if (area > largest_face_area) {
					largest_face_area = area;

					Handle(Geom_Surface) surf = BRep_Tool::Surface(TopoDS::Face(exp.Current()));
					if (surf->DynamicType() == STANDARD_TYPE(Geom_Plane)) {
						largest_face_dir = Handle(Geom_Plane)::DownCast(surf)->Axis().Direction();
						if (exp.Current().Orientation() == TopAbs_REVERSED) {
							largest_face_dir->Reverse();
						}
					}
				}
			}

			Bnd_Box box;
			double xyz[6];

			BRepBndLib::AddClose(compound, box);

			if (!box.IsVoid()) {
				box.Get(xyz[0], xyz[1], xyz[2], xyz[3], xyz[4], xyz[5]);
				for (int i = 0; i < 3; ++i) {
					const double bsz = xyz[i + 3] - xyz[i];
					put_json(BOUNDING_BOX_SIZE_ALONG_ + XYZ[i], bsz);
				}
			}
		}

		if (largest_face_dir) {
			put_json(LARGEST_FACE_DIRECTION, *largest_face_dir);
			put_json(LARGEST_FACE_AREA, largest_face_area);
		}
	}
};

int main () {
	// Redirect stdout to this stream, so that involuntary 
	// writes to stdout do not interfere with our protocol.
	std::ostringstream oss;
	stdout_redir = oss.rdbuf();
	stdout_orig = std::cout.rdbuf();
	std::cout.rdbuf(stdout_redir);

	bool emit_quantities = false;

#ifdef SET_BINARY_STREAMS
	_setmode(_fileno(stdout), _O_BINARY);
	std::cout.setf(std::ios_base::binary);
	_setmode(_fileno(stdin), _O_BINARY);
	std::cin.setf(std::ios_base::binary);
#endif

	double deflection = 1.e-3;
	bool has_more = false;

	IfcGeom::Iterator* iterator = 0;
	IfcParse::IfcFile* file = 0;
	std::vector< std::pair<uint32_t, uint32_t> > setting_pairs;

	Hello().write(std::cout);

	int exit_code = 0;
	for (;;) {
		const int32_t msg_type = sread<int32_t>(std::cin);
		switch (msg_type) {
		case IFC_MODEL: {
			IfcModel m; m.read(std::cin);
			std::string::size_type len = m.string().size();
			char* data = new char[len];
			memcpy(data, m.string().c_str(), len);

			ifcopenshell::geometry::Settings settings;
            settings.get<ifcopenshell::geometry::settings::UseWorldCoords>().value = false;
            settings.get<ifcopenshell::geometry::settings::WeldVertices>().value = false;
            settings.get<ifcopenshell::geometry::settings::ConvertBackUnits>().value = true;
            // settings.set(IfcGeom::IteratorSettings::INCLUDE_CURVES, true);

			/*
			// @todo
			std::vector< std::pair<uint32_t, uint32_t> >::const_iterator it = setting_pairs.begin();
			for (; it != setting_pairs.end(); ++it) {
				settings.get(it->first, it->second != 0);
				if (it->first == IfcGeom::IteratorSettings::SEW_SHELLS && it->second) {
					// Quantities (especially volume) can be emitted if there are proper
					// topologically valid geometries being created.
					emit_quantities = true;
				}
			}
			*/

			settings.get<ifcopenshell::geometry::settings::MesherLinearDeflection>().value = deflection;

			file = new IfcParse::IfcFile(data, (int)len);
			iterator = new IfcGeom::Iterator(settings, file);
			has_more = iterator->initialize();

			More(has_more).write(std::cout);
			continue;
		}
		case GET: {
			Get g; g.read(std::cin);
			if (!has_more) {
				exit_code = 1;
				break;
			}
			const IfcGeom::TriangulationElement* geom = static_cast<const IfcGeom::TriangulationElement*>(iterator->get());
			std::unique_ptr<EntityExtension> eext;
			if (emit_quantities) {
				eext.reset(new QuantityWriter_v1(iterator->get_native()));
			} else {
				eext.reset(new QuantityWriter_v0(iterator->get_native()));
			}
			Entity(geom, eext.get()).write(std::cout);
			continue;
		}
		case NEXT: {
			Next n; n.read(std::cin);
			has_more = iterator->next() != 0;
			if (!has_more) {
				delete file;
				delete iterator;
				file = 0;
				iterator = 0;
			}
			More(has_more).write(std::cout);
			continue;
		}
		case GET_LOG: {
			GetLog gl; gl.read(std::cin);
			WriteLog(Logger::GetLog()).write(std::cout);
			continue;
		}
		case BYE: {
			Bye().write(std::cout);
			exit_code = 0;
			break;
		}
		case DEFLECTION: {
			Deflection d; d.read(std::cin);
			if (!iterator) {
				deflection = d.deflection();
				continue;
			} else {
				exit_code = 1;
				break;
			}
		}
		case SETTING: {
			Setting s; s.read(std::cin);
			if (!iterator) {
				setting_pairs.push_back(std::make_pair(s.id(), s.value()));
				continue;
			} else {
				exit_code = 1;
				break;
			}
		}
		default:
			exit_code = 1; 
			break;
		}
		break;
	}
	std::cout.rdbuf(stdout_orig);
	return exit_code;
}
