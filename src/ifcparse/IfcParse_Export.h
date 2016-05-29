#ifndef IfcParse_EXPORT_H
#define IfcParse_EXPORT_H

#ifdef BUILD_SHARED_LIBS
  #ifdef _MSC_VER
    #ifdef IfcParse_EXPORTS
      #define IfcParse_EXPORT __declspec(dllexport)
    #else
      #define IfcParse_EXPORT __declspec(dllimport)
    #endif
  #else // simply assume GCC-like
    #define IfcParse_EXPORT __attribute__((visibility("default")))
  #endif
#else
  #define IfcParse_EXPORT
#endif

#endif
