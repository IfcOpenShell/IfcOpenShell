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

#if defined(_WIN32) && !defined(__CYGWIN__)
#define SET_BINARY_STREAMS
#endif
#ifdef SET_BINARY_STREAMS
#include <io.h>
#include <fcntl.h>
#endif

#include "../ifcgeom/IfcGeomObjects.h"

using namespace boost;

template <typename T>
T sread(std::istream& s) {
	char buf[sizeof(T)];
	s.read(buf, sizeof(T));
	return *((T*)buf);
}

template <>
std::string sread(std::istream& s) {
	int32_t len = sread<int32_t>(s);
	char* buf = new char[len + 1];
	s.read(buf, len);
	buf[len] = 0;
	while (len++ % 4) s.get();
	std::string str(buf);
	delete buf;
	return str;
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
	int32_t len = t.size();
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
	Hello() : Command(HELLO), str("IfcOpenShell-" IFCOPENSHELL_VERSION) {}
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
	void read_content(std::istream& s) {}
	void write_content(std::ostream& s) {}
public:
	Get() : Command(GET) {};
};

class GetLog : public Command {
protected:
	void read_content(std::istream& s) {}
	void write_content(std::ostream& s) {}
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

class Entity : public Command {
private:
	const IfcGeomObjects::IfcGeomObject* geom;
protected:
	void read_content(std::istream& s) {}
	void write_content(std::ostream& s) {
		swrite<int32_t>(s, geom->id());
		swrite(s, geom->guid());
		swrite(s, geom->name());
		swrite(s, geom->type());
		swrite<int32_t>(s, geom->parent_id());
		swrite(s, std::string((char*)geom->matrix().data(), 16 * sizeof(float)));
		swrite<int32_t>(s, geom->mesh().id());
		swrite(s, std::string((char*)geom->mesh().verts().data(), geom->mesh().verts().size() * sizeof(float)));
		swrite(s, std::string((char*)geom->mesh().normals().data(), geom->mesh().normals().size() * sizeof(float)));
		{ std::vector<int32_t> indices;
		for (std::vector<int>::const_iterator it = geom->mesh().faces().begin(); it != geom->mesh().faces().end(); ++it) {
			indices.push_back(*it);
		} 
		swrite(s, std::string((char*) indices.data(), indices.size() * sizeof(int32_t))); }
		{ std::vector<float> diffuse_color_array;
		for (std::vector<IfcGeomObjects::Material>::const_iterator it = geom->mesh().materials().begin(); it != geom->mesh().materials().end(); ++it) {
			const IfcGeomObjects::Material& m = *it;
			if (m.hasDiffuse()) {
				const double* color = m.diffuse();
				diffuse_color_array.push_back(static_cast<float>(color[0]));
				diffuse_color_array.push_back(static_cast<float>(color[1]));
				diffuse_color_array.push_back(static_cast<float>(color[2]));
			} else {
				diffuse_color_array.push_back(0.f);
				diffuse_color_array.push_back(0.f);
				diffuse_color_array.push_back(0.f);
			}
			if (m.hasTransparency()) {
				diffuse_color_array.push_back(static_cast<float>(1. - m.transparency()));
			} else {
				diffuse_color_array.push_back(1.f);
			}
		}
		swrite(s, std::string((char*) diffuse_color_array.data(), diffuse_color_array.size() * sizeof(float))); }
		{ std::vector<int32_t> material_indices;
		for (std::vector<int>::const_iterator it = geom->mesh().material_ids().begin(); it != geom->mesh().material_ids().end(); ++it) {
			material_indices.push_back(*it);
		} 
		swrite(s, std::string((char*) material_indices.data(), material_indices.size() * sizeof(int32_t))); }
	}
public:
	Entity(const IfcGeomObjects::IfcGeomObject* geom) : Command(ENTITY), geom(geom) {};
};

class Next : public Command {
protected:
	void read_content(std::istream& s) {}
	void write_content(std::ostream& s) {}
public:
	Next() : Command(NEXT) {};
};

class Bye : public Command {
protected:
	void read_content(std::istream& s) {}
	void write_content(std::ostream& s) {}
public:
	Bye() : Command(BYE) {};
};

int main (int argc, char** argv) {
	if (sizeof(float) != 4 || sizeof(int32_t) != 4) {
		return 1;
	}

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

	bool has_more = false;

	Hello().write(std::cout);

	int exit_code = 0;
	while (1) {
		const int32_t msg_type = sread<int32_t>(std::cin);
		switch (msg_type) {
		case IFC_MODEL: {
			IfcModel m; m.read(std::cin);
			std::string::size_type len = m.string().size();
			char* data = new char[len];
			memcpy(data, m.string().c_str(), len);

			IfcGeomObjects::Settings(IfcGeomObjects::USE_WORLD_COORDS, false);
			IfcGeomObjects::Settings(IfcGeomObjects::WELD_VERTICES, false);
			IfcGeomObjects::Settings(IfcGeomObjects::CONVERT_BACK_UNITS, true);
			IfcGeomObjects::Settings(IfcGeomObjects::FORCE_CCW_FACE_ORIENTATION, true);

			has_more = IfcGeomObjects::Init(data, len);
			More(has_more).write(std::cout);
			continue;
		}
		case GET: {
			Get g; g.read(std::cin);
			if (!has_more) {
				exit_code = 1;
				break;
			}
			const IfcGeomObjects::IfcGeomObject* geom = IfcGeomObjects::Get();
			Entity(geom).write(std::cout);
			continue;
		}
		case NEXT: {
			Next n; n.read(std::cin);
			has_more = IfcGeomObjects::Next();
			if (!has_more) {
				IfcGeomObjects::CleanUp();
			}
			More(has_more).write(std::cout);
			continue;
		}
		case GET_LOG: {
			GetLog gl; gl.read(std::cin);
			WriteLog(IfcGeomObjects::GetLog()).write(std::cout);
			continue;
		}
		case BYE: {
			Bye().write(std::cout);
			exit_code = 0;
			break;
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
