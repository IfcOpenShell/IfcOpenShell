
#ifndef HEADER_SECTION_SCHEMA_H
#define HEADER_SECTION_SCHEMA_H

#include <string>
#include <vector>

#include <boost/optional.hpp>

#include "../ifcparse/ifc_parse_api.h"

#include "../ifcparse/aggregate_of_instance.h"
#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/Argument.h"

struct Header_section_schema {

IFC_PARSE_API static const IfcParse::schema_definition& get_schema();

IFC_PARSE_API static void clear_schema();

static const char* const Identifier;

// Forward definitions
class file_description; class file_name; class file_schema; class schema_name; class time_stamp_text; 


class IFC_PARSE_API schema_name : public  IfcUtil::IfcBaseType {
public:
    virtual const IfcParse::type_declaration& declaration() const;
    static const IfcParse::type_declaration& Class();
    explicit schema_name (IfcEntityInstanceData&& e);
    schema_name (std::string v);
    operator std::string() const;
};

class IFC_PARSE_API time_stamp_text : public  IfcUtil::IfcBaseType {
public:
    virtual const IfcParse::type_declaration& declaration() const;
    static const IfcParse::type_declaration& Class();
    explicit time_stamp_text (IfcEntityInstanceData&& e);
    time_stamp_text (std::string v);
    operator std::string() const;
};



class IFC_PARSE_API file_description : public  IfcUtil::IfcBaseEntity {
public:
    std::vector< std::string > /*[1:?]*/ description() const;
    void setdescription(std::vector< std::string > /*[1:?]*/ v);
    std::string implementation_level() const;
    void setimplementation_level(std::string v);
        virtual const IfcParse::entity& declaration() const;
    static const IfcParse::entity& Class();
    file_description (IfcEntityInstanceData&& e);
    file_description (std::vector< std::string > /*[1:?]*/ v1_description, std::string v2_implementation_level);
    typedef aggregate_of< file_description > list;
};

class IFC_PARSE_API file_name : public  IfcUtil::IfcBaseEntity {
public:
    std::string name() const;
    void setname(std::string v);
    std::string time_stamp() const;
    void settime_stamp(std::string v);
    std::vector< std::string > /*[1:?]*/ author() const;
    void setauthor(std::vector< std::string > /*[1:?]*/ v);
    std::vector< std::string > /*[1:?]*/ organization() const;
    void setorganization(std::vector< std::string > /*[1:?]*/ v);
    std::string preprocessor_version() const;
    void setpreprocessor_version(std::string v);
    std::string originating_system() const;
    void setoriginating_system(std::string v);
    std::string authorization() const;
    void setauthorization(std::string v);
        virtual const IfcParse::entity& declaration() const;
    static const IfcParse::entity& Class();
    file_name (IfcEntityInstanceData&& e);
    file_name (std::string v1_name, std::string v2_time_stamp, std::vector< std::string > /*[1:?]*/ v3_author, std::vector< std::string > /*[1:?]*/ v4_organization, std::string v5_preprocessor_version, std::string v6_originating_system, std::string v7_authorization);
    typedef aggregate_of< file_name > list;
};

class IFC_PARSE_API file_schema : public  IfcUtil::IfcBaseEntity {
public:
    std::vector< std::string > /*[1:?]*/ schema_identifiers() const;
    void setschema_identifiers(std::vector< std::string > /*[1:?]*/ v);
        virtual const IfcParse::entity& declaration() const;
    static const IfcParse::entity& Class();
    file_schema (IfcEntityInstanceData&& e);
    file_schema (std::vector< std::string > /*[1:?]*/ v1_schema_identifiers);
    typedef aggregate_of< file_schema > list;
};

};

#endif
