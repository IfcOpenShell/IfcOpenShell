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

#include "../ifcgeom/IfcGeomIterator.h"

#if USE_VLD
#include <vld.h>
#endif

#include <GProp_GProps.hxx>
#include <BRepGProp.hxx>
#include <Geom_Plane.hxx>

using namespace boost;

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
	Hello() : Command(HELLO), str("IfcOpenShell-" IFCOPENSHELL_VERSION "-2") {}
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
public:
	virtual void write_contents(std::ostream& s) = 0;
};

class Entity : public Command {
private:
	const IfcGeom::TriangulationElement<float>* geom;
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
		const std::vector<float>& m = geom->transformation().matrix().data();
		const float matrix_array[16] = {
			m[0], m[3], m[6], m[ 9],
			m[1], m[4], m[7], m[10],
			m[2], m[5], m[8], m[11],
			   0,    0,    0,     1
		};
		swrite(s, std::string((char*)matrix_array, 16 * sizeof(float)));
		
		// The first bit of the string is always the instance name of the representation.
		const std::string& representation_id = geom->geometry().id();
		const int integer_representation_id = atoi(representation_id.c_str());
		swrite<int32_t>(s, (int32_t)integer_representation_id);

		swrite(s, std::string((char*)geom->geometry().verts().data(), geom->geometry().verts().size() * sizeof(float)));
		swrite(s, std::string((char*)geom->geometry().normals().data(), geom->geometry().normals().size() * sizeof(float)));
		{
			std::vector<int32_t> indices;
			const std::vector<int>& faces = geom->geometry().faces();
			indices.reserve(faces.size());
			for (std::vector<int>::const_iterator it = faces.begin(); it != faces.end(); ++it) {
				indices.push_back(*it);
			} 
			swrite(s, std::string((char*) indices.data(), indices.size() * sizeof(int32_t)));

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

				swrite(s, std::string((char*) lines.data(), lines.size() * sizeof(int32_t)));
			}
		}
		{ std::vector<float> diffuse_color_array;
		for (std::vector<IfcGeom::Material>::const_iterator it = geom->geometry().materials().begin(); it != geom->geometry().materials().end(); ++it) {
			const IfcGeom::Material& mat = *it;
			if (mat.hasDiffuse()) {
				const double* color = mat.diffuse();
				diffuse_color_array.push_back(static_cast<float>(color[0]));
				diffuse_color_array.push_back(static_cast<float>(color[1]));
				diffuse_color_array.push_back(static_cast<float>(color[2]));
			} else {
				diffuse_color_array.push_back(0.f);
				diffuse_color_array.push_back(0.f);
				diffuse_color_array.push_back(0.f);
			}
			if (mat.hasTransparency()) {
				diffuse_color_array.push_back(static_cast<float>(1. - mat.transparency()));
			} else {
				diffuse_color_array.push_back(1.f);
			}
		}
		swrite(s, std::string((char*) diffuse_color_array.data(), diffuse_color_array.size() * sizeof(float))); }
		{ std::vector<int32_t> material_indices;
		for (std::vector<int>::const_iterator it = geom->geometry().material_ids().begin(); it != geom->geometry().material_ids().end(); ++it) {
			material_indices.push_back(*it);
		} 
		swrite(s, std::string((char*) material_indices.data(), material_indices.size() * sizeof(int32_t))); }
		if (eext_) {
			eext_->write_contents(s);
		}
	}
public:
	Entity(const IfcGeom::TriangulationElement<float>* geom, EntityExtension* eext = 0) : Command(ENTITY), geom(geom), append_line_data(false), eext_(eext) {};
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
	Setting(uint32_t k = 0, uint32_t v = 0) : Command(DEFLECTION), id_(k), value_(v) {};
	uint32_t id() const { return id_; }
	uint32_t value() const { return value_; }
};

static const std::string TOTAL_SURFACE_AREA = "TOTAL_SURFACE_AREA";
static const std::string TOTAL_SHAPE_VOLUME = "TOTAL_SHAPE_VOLUME";
static const std::string WALKABLE_SURFACE_AREA = "WALKABLE_SURFACE_AREA";
static const double MAX_WALKABLE_SURFACE_ANGLE_DEGREES = 15.;

class QuantityWriter : public EntityExtension {
private:
	const IfcGeom::BRepElement<float>* elem_;
public:
	QuantityWriter(const IfcGeom::BRepElement<float>* elem) :
		elem_(elem)
	{}
	void write_contents(std::ostream& s) {
		
		double total_surface_area = 0.;
		double total_shape_volume = 0.;
		double walkable_surface_area = 0.;

		for (IfcGeom::IfcRepresentationShapeItems::const_iterator it = elem_->geometry().begin(); it != elem_->geometry().end(); ++it) {
			gp_GTrsf gtrsf = it->Placement();
			const gp_Trsf& o_trsf = elem_->transformation().data();
			gtrsf.PreMultiply(o_trsf);
			const TopoDS_Shape& shp = it->Shape();
			const TopoDS_Shape moved_shape = IfcGeom::Kernel::apply_transformation(shp, gtrsf);
			
			{
				GProp_GProps prop_area;
				BRepGProp::SurfaceProperties(moved_shape, prop_area);
				total_surface_area += prop_area.Mass();
			}

			{
				GProp_GProps prop_volume;
				BRepGProp::VolumeProperties(moved_shape, prop_volume);
				total_shape_volume += prop_volume.Mass();
			}

			if (elem_->type() == "IfcSpace") {
				TopExp_Explorer exp(moved_shape, TopAbs_FACE);
				for (; exp.More(); exp.Next()) {
					const TopoDS_Face& face = TopoDS::Face(exp.Current());
					Handle(Geom_Surface) surf = BRep_Tool::Surface(face);

					// Assume we can only walk on planar surfaces
					if (surf->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
						continue;
					}

					BRepGProp_Face prop(face);
					double u0, u1, v0, v1;
					BRepTools::UVBounds(face, u0, u1, v0, v1);
					gp_Pnt p;
					gp_Vec normal_direction;
					prop.Normal((u0 + u1) / 2., (v0 + v1) / 2., p, normal_direction);

					gp_Vec normal(0., 0., 0.);
					if (normal_direction.Magnitude() > ALMOST_ZERO) {
						normal = gp_Dir(normal_direction.XYZ());
					}

					if (normal.Angle(gp::DZ()) < (MAX_WALKABLE_SURFACE_ANGLE_DEGREES * M_PI / 180.0)) {
						GProp_GProps prop_face;
						BRepGProp::SurfaceProperties(face, prop_face);
						walkable_surface_area += prop_face.Mass();
					}
				}
			}
		}
		
		// TODO: Manual JSON formatting is always a bad idea
		std::ostringstream ss;
		ss.write("{", 1);
		ss << format_json(TOTAL_SURFACE_AREA);
		ss.write(":", 1);
		ss << format_json(total_surface_area);
		ss.write(",", 1);
		ss << format_json(TOTAL_SHAPE_VOLUME);
		ss.write(":", 1);
		ss << format_json(total_shape_volume);
		if (elem_->type() == "IfcSpace") {
			ss.write(",", 1);
			ss << format_json(WALKABLE_SURFACE_AREA);
			ss.write(":", 1);
			ss << format_json(walkable_surface_area);
		}
		ss.write("}", 1);

		// We do a 4-byte manual alignment
		std::string payload = ss.str();
		s << payload;
		if (payload.size() % 4) {
			s << std::string(4 - (payload.size() % 4), ' ');
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

#ifdef SET_BINARY_STREAMS
	_setmode(_fileno(stdout), _O_BINARY);
	std::cout.setf(std::ios_base::binary);
	_setmode(_fileno(stdin), _O_BINARY);
	std::cin.setf(std::ios_base::binary);
#endif

	double deflection = 1.e-3;
	bool has_more = false;

	IfcGeom::Iterator<float>* iterator = 0;
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

			IfcGeom::IteratorSettings settings;
            settings.set(IfcGeom::IteratorSettings::USE_WORLD_COORDS, false);
            settings.set(IfcGeom::IteratorSettings::WELD_VERTICES, false);
            settings.set(IfcGeom::IteratorSettings::CONVERT_BACK_UNITS, true);
            // settings.set(IfcGeom::IteratorSettings::INCLUDE_CURVES, true);

			std::vector< std::pair<uint32_t, uint32_t> >::const_iterator it = setting_pairs.begin();
			for (; it != setting_pairs.end(); ++it) {
				settings.set(it->first, it->second != 0);
			}

			settings.set_deflection_tolerance(deflection);

			iterator = new IfcGeom::Iterator<float>(settings, data, (int)len);
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
			const IfcGeom::TriangulationElement<float>* geom = static_cast<const IfcGeom::TriangulationElement<float>*>(iterator->get());
			QuantityWriter eext(iterator->get_native());
			Entity(geom, &eext).write(std::cout);
			continue;
		}
		case NEXT: {
			Next n; n.read(std::cin);
			has_more = iterator->next() != 0;
			if (!has_more) {
				delete iterator;
				iterator = 0;
			}
			More(has_more).write(std::cout);
			continue;
		}
		case GET_LOG: {
			GetLog gl; gl.read(std::cin);
			WriteLog(iterator->getLog()).write(std::cout);
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
