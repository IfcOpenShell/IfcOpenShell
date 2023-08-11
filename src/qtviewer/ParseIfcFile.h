#ifndef PARSEIFCFILE_H
#define PARSEIFCFILE_H

#include <string>

class ParseIfcFile
{
public:
    ParseIfcFile();
    ~ParseIfcFile();

    void Parse(const std::string& filePath);
};

#endif // PARSEIFCFILE_H