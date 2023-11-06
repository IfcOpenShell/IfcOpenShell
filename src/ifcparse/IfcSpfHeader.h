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

#ifndef IFCSPFHEADER_H
#define IFCSPFHEADER_H

#include "ifc_parse_api.h"
#include "IfcWrite.h"

namespace IfcParse {

class IFC_PARSE_API HeaderEntity : public IfcEntityInstanceData {
  private:
    const char* const datatype_;
    size_t size_;

    HeaderEntity(const HeaderEntity&);            //N/A
    HeaderEntity& operator=(const HeaderEntity&); //N/A
  protected:
    HeaderEntity(const char* const datatype, size_t size, IfcParse::IfcFile* file);
    virtual ~HeaderEntity();

    void setValue(unsigned int i, const std::string& s) {
        IfcWrite::IfcWriteArgument* argument = new IfcWrite::IfcWriteArgument;
        argument->set(s);
        setArgument(i, argument);
    }

    void setValue(unsigned int i, const std::vector<std::string>& s) {
        IfcWrite::IfcWriteArgument* argument = new IfcWrite::IfcWriteArgument;
        argument->set(s);
        setArgument(i, argument);
    }

  public:
    virtual size_t getArgumentCount() const {
        return size_;
    }

    std::string toString(bool upper = false) const {
        std::stringstream ss;
        ss << datatype_ << IfcEntityInstanceData::toString(upper);
        return ss.str();
    }
};

class IFC_PARSE_API FileDescription : public HeaderEntity {
  public:
    explicit FileDescription(IfcFile* = 0);

    std::vector<std::string> description() const { return *getArgument(0); }
    std::string implementation_level() const { return *getArgument(1); }

    void description(const std::vector<std::string>& value) { setValue(0, value); }
    void implementation_level(const std::string& value) { setValue(1, value); }
};

class IFC_PARSE_API FileName : public HeaderEntity {
  public:
    explicit FileName(IfcFile* = 0);

    std::string name() const { return *getArgument(0); }
    std::string time_stamp() const { return *getArgument(1); }
    std::vector<std::string> author() const { return *getArgument(2); }
    std::vector<std::string> organization() const { return *getArgument(3); }
    std::string preprocessor_version() const { return *getArgument(4); }
    std::string originating_system() const { return *getArgument(5); }
    std::string authorization() const { return *getArgument(6); }

    void name(const std::string& value) { setValue(0, value); }
    void time_stamp(const std::string& value) { setValue(1, value); }
    void author(const std::vector<std::string>& value) { setValue(2, value); }
    void organization(const std::vector<std::string>& value) { setValue(3, value); }
    void preprocessor_version(const std::string& value) { setValue(4, value); }
    void originating_system(const std::string& value) { setValue(5, value); }
    void authorization(const std::string& value) { setValue(6, value); }
};

class IFC_PARSE_API FileSchema : public HeaderEntity {
  public:
    explicit FileSchema(IfcFile* = 0);

    std::vector<std::string> schema_identifiers() const { return *getArgument(0); }

    void schema_identifiers(const std::vector<std::string>& value) { setValue(0, value); }
};

class IFC_PARSE_API IfcSpfHeader {
  private:
    IfcFile* file_;
    FileDescription* file_description_;
    FileName* file_name_;
    FileSchema* file_schema_;
    void readParen();
    void readSemicolon();
    enum Trail {
        TRAILING_SEMICOLON,
        TRAILING_PAREN,
        NONE
    };
    void readTerminal(const std::string& term, Trail trail);

  public:
    explicit IfcSpfHeader(IfcParse::IfcFile* file = 0)
        : file_(file),
          file_description_(0),
          file_name_(0),
          file_schema_(0) {
        file_description_ = new FileDescription(file_);
        file_name_ = new FileName(file_);
        file_schema_ = new FileSchema(file_);
    }

    ~IfcSpfHeader() {
        delete file_schema_;
        delete file_name_;
        delete file_description_;
    }

    IfcParse::IfcFile* file() { return file_; }
    void file(IfcParse::IfcFile* file) { file_ = file; }

    void read();
    bool tryRead();

    void write(std::ostream& os) const;

    const FileDescription& file_description() const;
    const FileName& file_name() const;
    const FileSchema& file_schema() const;

    FileDescription& file_description();
    FileName& file_name();
    FileSchema& file_schema();
};

} // namespace IfcParse

#endif
