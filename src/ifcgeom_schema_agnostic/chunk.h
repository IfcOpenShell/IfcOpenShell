// Chunk.h
#ifndef CHUNK_H
#define CHUNK_H

#include <vector>

namespace IfcGeom {
    struct chunk {
        std::vector<std::string> guids;
        std::vector<int> guid_ids;
        std::vector<double> verts;
        std::vector<int> faces;
        std::vector<int> materials;
        std::vector<int> material_ids;
        std::vector<std::vector<float>> colours;
    };
}

#endif
