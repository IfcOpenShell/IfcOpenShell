// This file was generated with the assistance of an AI coding tool.
import { ifcopenshell } from '../init.js';
import type { settings } from './settings.js';
import type { entity_instance } from '../entity_instance.js';

/** Create one shape. Load the schema mapping and geometry kernel beforehand. */
export function create_shape(settings: settings, instance: entity_instance, representation?: entity_instance, geometry_library = 'opencascade') {
  return ifcopenshell.geom.createShape(settings, instance, representation ?? null, geometry_library);
}
