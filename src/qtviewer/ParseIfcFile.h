#ifndef PARSEIFCFILE_H
#define PARSEIFCFILE_H

#include <QObject>
#include <QString>
#include <string>

class ParseIfcFile : public QObject
{
public:
    ParseIfcFile();
    ~ParseIfcFile();

    void Parse(const std::string& filePath);
};

#endif // PARSEIFCFILE_H
