#ifndef PARSEIFCFILE_H
#define PARSEIFCFILE_H

#include <QObject>
#include <QString>
#include <string>

class ParseIfcFile : public QObject
{
    Q_OBJECT

signals:
    void parsingInfo(const QString& info);

private:
    void outputMsg(const std::string& msg);

public:
    ParseIfcFile();
    ~ParseIfcFile();

    void Parse(const std::string& filePath);
};

#endif // PARSEIFCFILE_H