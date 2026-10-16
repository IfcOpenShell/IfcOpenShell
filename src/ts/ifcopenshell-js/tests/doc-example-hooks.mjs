// This file was generated with the assistance of an AI coding tool.

const packaged = {
  ifcopenshell: '../dist/index.js',
  'ifcopenshell/geom': '../dist/geom/index.js',
  'ifcopenshell/serializers': '../dist/serializers/index.js',
  'ifcopenshell/util': '../dist/util/index.js',
};

export async function resolve(specifier, context, nextResolve) {
  const target = packaged[specifier];
  if (target) {
    return {
      shortCircuit: true,
      url: new URL(target, import.meta.url).href,
    };
  }
  return nextResolve(specifier, context);
}
