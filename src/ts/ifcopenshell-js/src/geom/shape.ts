// This file was generated with the assistance of an AI coding tool.
import { ifcopenshell } from '../init.js';
import type { Settings } from './settings.js';
import type { EntityInstance } from '../entity_instance.js';

/** Create one shape. Load the schema mapping and geometry kernel beforehand. */
export function createShape(settings: Settings, instance: EntityInstance, representation?: EntityInstance, geometryLibrary = 'opencascade') {
  return ifcopenshell.geom.createShape(settings, instance, representation ?? null, geometryLibrary);
}
