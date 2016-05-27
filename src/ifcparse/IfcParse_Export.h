#ifndef IfcParse_EXPORT_H
#define IfcParse_EXPORT_H

#ifdef IFCPARSE_STATIC_DEFINE
  #define IfcParse_EXPORT
#else
  #ifdef _WIN32
    #ifndef IfcParse_EXPORT
      #ifdef IfcParse_EXPORTS
        #define IfcParse_EXPORT __declspec(dllexport)
      #else
        #define IfcParse_EXPORT __declspec(dllimport)
      #endif
    #endif
  #elif __linux__
    #define IfcParse_EXPORT __attribute__((visibility("default")))
  #else
    #define IfcParse_EXPORT
  #endif
#endif

#endif
