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

/********************************************************************************
*                                                                              *
* This is a JNI interface to IfcOpenShell for use with the open source         *
* http://BIMserver.org                                                         *
*                                                                              *
********************************************************************************/

#include "org_ifcopenshell_IfcOpenShellModel.h"
#include "../ifcgeom/IfcGeomObjects.h"

static bool has_more = false;

JNIEXPORT jobject JNICALL Java_org_ifcopenshell_IfcOpenShellModel_getGeometry (JNIEnv * env, jobject) {
	if ( ! has_more ) return 0;
	jclass class_def = env->FindClass ("org/ifcopenshell/IfcGeomObject");
	if ( ! class_def ) return 0;
	jmethodID jconstructor = env->GetMethodID(class_def, "<init>", "(ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;[I[F[F)V");
	if ( ! jconstructor ) return 0;
	const IfcGeomObjects::IfcGeomObject* o = IfcGeomObjects::Get();

	jstring name = env->NewStringUTF(o->name().c_str());
	jstring type = env->NewStringUTF(o->type().c_str());
	jstring guid = env->NewStringUTF(o->guid().c_str());

	jintArray indices = env->NewIntArray(o->mesh().faces().size());
	jfloatArray positions = env->NewFloatArray(o->mesh().verts().size());
	jfloatArray normals = env->NewFloatArray(o->mesh().normals().size());

	env->SetIntArrayRegion(indices,0,o->mesh().faces().size(),(jint*) &o->mesh().faces()[0]);
	env->SetFloatArrayRegion(positions,0,o->mesh().verts().size(),(jfloat*) &o->mesh().verts()[0]);
	env->SetFloatArrayRegion(normals,0,o->mesh().normals().size(),(jfloat*) &o->mesh().normals()[0]);

	jobject return_obj = env->NewObject(class_def, jconstructor, o->id(), name, type, guid, indices, positions, normals);

	env->DeleteLocalRef(name);
	env->DeleteLocalRef(type);
	env->DeleteLocalRef(guid);
	env->DeleteLocalRef(indices);
	env->DeleteLocalRef(positions);
	env->DeleteLocalRef(normals);
	env->DeleteLocalRef(class_def);

	has_more = IfcGeomObjects::Next();
	if ( ! has_more ) IfcGeomObjects::CleanUp();

	return return_obj;
}

JNIEXPORT jboolean JNICALL Java_org_ifcopenshell_IfcOpenShellModel_setIfcData (JNIEnv * env, jobject, jbyteArray jdata) {
	if ( ! jdata ) return false;
	const int length = env->GetArrayLength(jdata);
	jboolean is_copy = false;
	jbyte* jbytes = env->GetByteArrayElements(jdata, &is_copy);
	if ( ! jbytes || ! length ) return false;
	void* data = new char[length];
	memcpy(data,jbytes,length);
	env->ReleaseByteArrayElements(jdata, jbytes, JNI_ABORT);
	IfcGeomObjects::Settings(IfcGeomObjects::USE_WORLD_COORDS, true);
	IfcGeomObjects::Settings(IfcGeomObjects::WELD_VERTICES, false);
	IfcGeomObjects::Settings(IfcGeomObjects::CONVERT_BACK_UNITS, true);
	return has_more = IfcGeomObjects::Init(data, length);
}

JNIEXPORT jstring JNICALL Java_org_ifcopenshell_IfcOpenShellModel_getPluginVersion (JNIEnv * env, jobject) {
	return env->NewStringUTF(IFCOPENSHELL_VERSION);
}