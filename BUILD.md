    conan create . -pr=.conan/profiles/linux_release --build missing
    conan install . -pr=.conan/profiles/linux_debug --build missing
conan install . -pr:h=default -pr:b=.conan/profiles/wasm_release --build missing
conan build . -pr:h=default -pr:b=.conan/profiles/wasm_release --build missing

TODO:
- have shared build works in conan center
- have OpenUSD in conan center (https://github.com/conan-io/conan-center-index/pull/24506)
- have onetbb build statically in conan center
- Add message(STATUS ...) of options
- have current PRs merged:
  
    https://github.com/IfcOpenShell/IfcOpenShell/pull/7436
    https://github.com/IfcOpenShell/IfcOpenShell/pull/7434
  
- have latest opencascade in conan center (https://github.com/conan-io/conan-center-index/pull/27354)

- compare different web ifc viewer:
  https://github.com/ThatOpen/engine_components
  https://github.com/viktor-platform/ifc-viewer/tree/master
  https://view.ifcopenshell.org/v/nVKkFOmbzjTaaUXnijHDHbDyXIHBSjyF

- Add wasm build through conan 
- Add ifcwrap build through conan
- Set cmake scope (PUBLIC/PRIVATE)
- Study mmap (https://www.boost.org/doc/libs/latest/libs/iostreams/doc/classes/mapped_file.html) from boost used in ifcparse and ifcconvert
- Study WITH_RELATIONSHIP_VALIDATION option
- Study hdf5 used by ifcgeom/serializers/ifcconvert

Study https://github.com/Krande

Study MCP and see how to apply it to IfcOpenShell (https://modelcontextprotocol.io/docs/learn/client-concepts)