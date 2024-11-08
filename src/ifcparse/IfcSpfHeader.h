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
#include "IfcEntityInstanceData.h"

namespace IfcParse {
    class IfcFile;

class IFC_PARSE_API HeaderEntity {
  private:
    const char* const datatype_;
    IfcFile* file_;
    
    HeaderEntity(const HeaderEntity&);            //N/A
    HeaderEntity& operator=(const HeaderEntity&); //N/A
  protected:
      IfcEntityInstanceData data_;

    HeaderEntity(const char* const datatype, size_t size, IfcParse::IfcFile* file);
    virtual ~HeaderEntity();

    void setValue(unsigned int index, const std::string& string) {
        data_.storage_.set(index, string);
    }

    void setValue(unsigned int index, const std::vector<std::string>& strings) {
        data_.storage_.set(index, strings);
    }

  public:
    virtual size_t getArgumentCount() const {
        return data_.size();
    }

    AttributeValue getArgument(size_t index) const {
        return data_.get_attribute_value(index);
    }

    std::string toString(bool upper = false) const {
        std::stringstream stream;
        stream << datatype_;
        data_.toString(stream, upper);
        return stream.str();
    }
};

class IFC_PARSE_API FileDescription : public HeaderEntity {
  public:
    explicit FileDescription(IfcFile* = 0);

    std::vector<std::string> description() const { return data_.get_attribute_value(0); }
    std::string implementation_level() const { return data_.get_attribute_value(1); }

    void description(const std::vector<std::string>& value) { setValue(0, value); }
    void implementation_level(const std::string& value) { setValue(1, value); }
};

class IFC_PARSE_API FileName : public HeaderEntity {
  public:
    explicit FileName(IfcFile* = 0);

    std::string name() const { return data_.get_attribute_value(0); }
    std::string time_stamp() const { return data_.get_attribute_value(1); }
    std::vector<std::string> author() const { return data_.get_attribute_value(2); }
    std::vector<std::string> organization() const { return data_.get_attribute_value(3); }
    std::string preprocessor_version() const { return data_.get_attribute_value(4); }
    std::string originating_system() const { return data_.get_attribute_value(5); }
    std::string authorization() const { return data_.get_attribute_value(6); }

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

    std::vector<std::string> schema_identifiers() const { return data_.get_attribute_value(0); }

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
    explicit IfcSpfHeader(IfcParse::IfcFile* file = nullptr)
        : file_(file),
          file_description_(0),
          file_name_(0),
          file_schema_(0)
    {
        if (file == nullptr) {
            file_description_ = new FileDescription(file_);
            file_name_ = new FileName(file_);
            file_schema_ = new FileSchema(file_);
        }
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

    void write(std::ostream& out) const;

    const FileDescription& file_description() const;
    const FileName& file_name() const;
    const FileSchema& file_schema() const;

    FileDescription& file_description();
    FileName& file_name();
    FileSchema& file_schema();
};

} // namespace IfcParse

#endif
