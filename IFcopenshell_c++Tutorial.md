# IFCopenshell Tuotorial In c++ Version|Beginner
>This tuotorial is aiming to introduce how to utilize **IfcopenShell** in **c++** with Visual Studio, I will introduce how to extracte **IFC Direct attribute**、**inverse attribute** and **Geometry coordination**.     
Before Reading this doc, please make sure you have **acquainted with basic Ifc Structure Info** from Ifc offcial document.  

# Ifc Direct Attribute  
Ifcopenshell provide easy-to-use parse function,so that we just need to think about what entity we wanna know.  
For example, I do interested in **IfcDuctSegment in domain schema**,I just need to exchange entity type in sample date,which comes from **Ifcopensehll.sln -example modle-IfcParse.CPP file**.
> It may be **Ifcwall** entity in **IFcParse.cpp file**  cause I am not sure about it. Anyway you shall change IFcwall to what you want.  🤣🤣

➡️Here is the sample code:
```	
IfcSchema::IfcDuctSegment::list::ptr ductsegment = file.instances_by_type<IfcSchema::IfcDuctSegment>();  
	for (IfcSchema::IfcDuctSegment::list::it it = ductsegment->begin(); it != ductsegment->end(); ++it)  
	{
		const IfcSchema::IfcDuctSegment* master = *it;
		std::cout << master->data().toString() << std::endl;
	}  
```

# Ifc Inverse Attribute
[IfcDuctSegment](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/) Web link is here ,you shall know its inverse attrribute from here, following content will focus on that so you'd better take a look.  
 IfcDuctSegment has so many parent relationship as an entity such as Ifcroot、IfcObjectDefinition and so on(*see IfcDuctSegment hierachy* ).To explain how to get its inverse attribute i will focus on its **IsDefinedBy** attribute in this chapter.
> **IfcDuctSegment hierachy**  
Ifcroot->IfcObjectDefinition->IfcObject->IfcProduct->IfcElement->IfcDistributionElement->IfcDistributionFlowElement->IfcFlowElement->IfcDuctSegment  

IfcDuctSegment's IsDefinedBy contains lots of proerty in this entity,it describes the relationship among material、type and soon.  

> **IsDefinedBy**:The objectified relationship IfcRelDefinesByProperties defines the relationships between property set definitions and objects. Properties are aggregated in property sets. Property sets can be either directly assigned to occurrence objects using this relationship, or assigned to an object type and assigned via that type to occurrence objects.    

based on object-code paradigm,inverse-attribute is a king of class in this code , we shall to declare a Varibale of **::Ifc4::IfcRelDefinesByProperties::list::ptr**,then we utilize **IsDefinedBy** method to extracte Defined property in this **Proertiest::list** if IfcDusegemnt property_set is not null.  
## Why list?  
cause source code has defined each property_set will be store in **aggreration of (TYPE) list**,sothat we must access property_set from this list.  
todo:copy source code of IfcRelDefinesByProperties type.

```	
{
		::Ifc4::IfcRelDefinesByProperties::list::ptr RelProperty = master->IsDefinedBy();
		for (auto property : *RelProperty)
		{
			
			std::string content = property->RelatingPropertyDefinition()->data().toString();
			outputFile << property->RelatingPropertyDefinition()->data().toString() << std::endl;
			
		}
}
```
## Output Sample
todo:show up output sample code with **instance_by_id** method
# Geometry coordination point   
Geometry coordination is a very important element for 3-dimensiton Rebuild and Geomotry calculation. As far as I know about topography info about IfcductSegment, I split process to 3 steps:  
1. Get instance's ptr at first.   
2. extracte **#Id** by regex fucntion.  
3. utilize  **```instace_by_id``` method**,then do it with loops until getting our position Info.   
> maybe loops take 4 times or 5 times ,it's depends on the entity'topology relationship which you are interested in.  
**By the way,If you have any better idea please share to talk with me,my pleasure!** 😁   

Next following will share my demo to talk about how to extracte IfcFlowTerminal entities' Geometry Info from Ifc4 file  by regex method.  
1. import necessary headfile and **#define IfcSchema Ifc4**.
2. make sure what outputPath you are decided,common choice are console_interface and local file.   
```
console_interface

Logger::SetOutput(&std::cout, &std::cout);
local file  

std::ofstream outputFile("geometric_test.txt");
 Logger::SetOutput(&outputFile, &outputFile);
 ```
3. access IfcFlowTerminal entity with loop to find out instance while the number of instance is not null. 
4. regex method as followed. 
# Demo_code

```#include<iostream>
#define IfcSchema Ifc4
#include<ostream>
#include<regex>
#include<vector>
#include<fstream>
#include<string>
#include "../../IfcOpenshell/src/ifcparse/IfcFile.h"
#include "../../IfcOpenshell/src/ifcparse/Ifc4.h"

#if USE_VLD
    #include <vld.h>
    #endif
    int main()
    {
	


	std::string Ifcfile = "Your Ifc file path";
	IfcParse::IfcFile file = Ifcfile;

	std::ofstream outputFile("geometric_test.txt");

	if (!outputFile.is_open()) {
		std::cout << "Unable to open output file" << std::endl;
		return 1;
	}
	Logger::SetOutput(&outputFile, &outputFile);

	if (!file.good()) {

		std::cout << "Unable to parse .ifc file" << std::endl;
		return 1;
	}
	
	std::cout << "------------begin--------------" << std::endl;
	IfcSchema::IfcFlowTerminal::list::ptr IfcFlowTerminal_instance = file.instances_by_type< IfcSchema::IfcFlowTerminal>();
	for (IfcSchema::IfcFlowTerminal::list::it it = IfcFlowTerminal_instance->begin(); it != IfcFlowTerminal_instance->end(); ++it)
	{
		const IfcSchema::IfcFlowTerminal* master = *it;

		std::cout<< master->data().toString()<<std::endl;
		

		std:: string input = master->data().toString();
		std::istringstream iss(input);

		std::string token;
		int count=0;
		int IfcProductDefinitionShape_id =0;
		while (std::getline(iss, token, ','))
		{
			if (token.find('#') == 0)
			{
				++count;
				if (count == 4)
				{
					std::cout << "IfcProductDefinitionShape_id :	" << token << std::endl;	
					IfcProductDefinitionShape_id = std::stoi(token.substr(1));

					break;
				}
			}
		}
		
		IfcUtil::IfcBaseClass* IfcProductDefinitionShape_instance = file.instance_by_id(IfcProductDefinitionShape_id);
	
		std::string input1 = IfcProductDefinitionShape_instance->data().toString();
		
		std::cout << input1 << std::endl;
		
		
		std::regex pattern("#[0-9]+");
		std::sregex_iterator iter(input1.begin(), input1.end(), pattern);
		std::sregex_iterator end;
		std::vector<int>IfcShapeRepresentation_IdList;

		while (iter != end) {
			std::smatch match = *iter;
			std::string result = match.str().substr(1); 
			IfcShapeRepresentation_IdList.push_back(std::stoi(result));
			++iter;
		}
		int IfcShapeRepresentation_id = IfcShapeRepresentation_IdList[1];
		std::cout << "IfcShapeRepresentation_id:	" << IfcShapeRepresentation_id << std::endl;
		
		

		//reading ifcMappedItem
		IfcUtil::IfcBaseClass* IfcShapeRepresentation_instance = file.instance_by_id(IfcShapeRepresentation_id);
		std::string input2 = IfcShapeRepresentation_instance->data().toString();
		std::cout << input2 << std::endl;

		std::sregex_iterator iter1(input2.begin(), input2.end(), pattern);
		std::sregex_iterator end1;
		std::vector<int>IfcMappedItem_IdList;

		while (iter1 != end1) {
			std::smatch match1 = *iter1;
			std::string result = match1.str().substr(1); 
			IfcMappedItem_IdList.push_back(std::stoi(result));
			++iter1;
		}
		int IfcMappedItem_id = IfcMappedItem_IdList[2];
		std::cout << "IfcMappedItem_id:	" << IfcMappedItem_id << std::endl;
	

		//reading IfcShapeRepresentation's Geometry and its inverse attribut  
		IfcUtil::IfcBaseClass* IfcMappedItem_instance = file.instance_by_id(IfcMappedItem_id);
		std::cout << IfcMappedItem_instance->data().toString() << std::endl;
		std::string input3 = IfcMappedItem_instance->data().toString();
		std::sregex_iterator iter2(input3.begin(), input3.end(), pattern);
		std::sregex_iterator end2;
		std::vector<int>IfcRepresentationMap_IdList;
		while (iter2 != end2) {
			std::smatch match2 = *iter2;
			std::string result = match2.str().substr(1); 
			IfcRepresentationMap_IdList.push_back(std::stoi(result));
			++iter2;
		}
		int IfcRepresentationMap_id = IfcRepresentationMap_IdList[1];
		std::cout << "ifcRepresentationMap_id:	" << IfcRepresentationMap_id << std::endl;
	
		
		//extracte Geometry position
		IfcUtil::IfcBaseClass* IfcRepresentationMap_instance = file.instance_by_id(IfcRepresentationMap_id);
		std::cout << IfcRepresentationMap_instance->data().toString() << std::endl;
		std::string input4 = IfcRepresentationMap_instance->data().toString();
		std::sregex_iterator iter3(input4.begin(), input4.end(), pattern);
		std::sregex_iterator end3;
		std::vector<int>GeoInfo_List;
		while (iter3 != end3) {
			std::smatch match3 = *iter3;
			std::string result = match3.str().substr(1);
			GeoInfo_List.push_back(std::stoi(result));
			++iter3;
		}
		
		//
		for (int i = 2; i < GeoInfo_List.size(); i++)
		{
			std::cout << "IfcShapeRepresentation_id:	" << GeoInfo_List[2] << std::endl;
			IfcUtil::IfcBaseClass* IFcPoint_set = file.instance_by_id(GeoInfo_List[i]);
			std::cout << IFcPoint_set->data().toString() << std::endl;
			std::string input5 = IFcPoint_set->data().toString();
			std::sregex_iterator iter4(input5.begin(), input5.end(), pattern);
			std::sregex_iterator end4;
			std::vector<int>Point_instance;
			while (iter4 != end4) {
				std::smatch match4 = *iter4;
				std::string result = match4.str().substr(1); 
				Point_instance.push_back(std::stoi(result));
				++iter4;
				
			}
			for (int j = 2; j < Point_instance.size(); j++)
			{
				IfcUtil::IfcBaseClass* point = file.instance_by_id(Point_instance[j]);
				std::cout << point->data().toString() << std::endl;
			}
			std::cout << "-------------------" << std::endl;
		
		}
	}
	outputFile.close();
	

	return 0;
	
}
```
# Reference
[IfcOpenshell_Offcial_doc]()  
[c++ regex]()  
[IfcOpenshell_issue]()

# Tool
[IfcOpenViewer]()  
