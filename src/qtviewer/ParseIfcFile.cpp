#include "ParseIfcFile.h"

#include "../ifcgeom_schema_agnostic/IfcGeomIterator.h"

ParseIfcFile::ParseIfcFile() {}

ParseIfcFile::~ParseIfcFile() {}

void ParseIfcFile::outputMsg(const std::string& msg)
{
	emit parsingInfo(QString::fromStdString(msg));
}

void ParseIfcFile::Parse(const std::string& filePath)
{
    IfcParse::IfcFile file(filePath);

    IfcGeom::IteratorSettings settings;
    settings.set(IfcGeom::IteratorSettings::USE_WORLD_COORDS, true);
    settings.set(IfcGeom::IteratorSettings::WELD_VERTICES, false);

    IfcGeom::Iterator* it = new IfcGeom::Iterator(settings, &file);
    if (!it->initialize()) {
        outputMsg("Error: Iterator failed to initialize! Aborting.");
        delete it;
        return;
    }

    do {
        //const IfcGeom::BRepElement* bRepElem = it->get_native();
        const IfcGeom::TriangulationElement* triElem = static_cast<const IfcGeom::TriangulationElement*>(it->get());
        outputMsg(triElem->type() + ": " + triElem->name());

        const boost::shared_ptr<IfcGeom::Representation::Triangulation>& triElemGeom = triElem->geometry_pointer();

        // materials
        const std::vector<IfcGeom::Material>& elemMats = triElemGeom->materials();
        for (auto mat : elemMats) {
            outputMsg("    " + mat.original_name());
        }
    } while (it->next());
}