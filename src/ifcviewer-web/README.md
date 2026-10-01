conan install . -pr:h=../../.conan2/profiles/emscripten_host -pr:b=../../.conan2/profiles/linux_host
conan build . -pr:h=../../.conan2/profiles/emscripten_host -pr:b=../../.conan2/profiles/linux_host
conan export-pkg . -pr:h=../../.conan2/profiles/emscripten_host -pr:b=../../.conan2/profiles/linux_host

// Alternative: use conan create
conan create . -pr:h=../../.conan2/profiles/emscripten_host -pr:b=../../.conan2/profiles/linux_host

conan install --requires=ifcviewer-web/0.1.0 \
  -pr:h=../../.conan2/profiles/emscripten_host -pr:b=../../.conan2/profiles/linux_host \
  --deployer=direct_deploy --deployer-folder=npm-pkg

cd npm-pkg/direct-deploy/ifcviewer-web
echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc
npm publish --access public