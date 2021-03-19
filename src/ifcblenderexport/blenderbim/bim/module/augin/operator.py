import os
import bpy
import json
import string
import random
import shutil
import requests
import tempfile
import datetime
import addon_utils


class AuginLogin(bpy.types.Operator):
    bl_idname = "bim.augin_login"
    bl_label = "Login to Augin"

    def execute(self, context):
        props = bpy.context.scene.AuginProperties

        url = "https://server.auge.pro.br/API/v3/augin_rest.php/user_login"
        payload = {"email": props.username, "password": props.password}
        response = requests.request("POST", url, data=payload)
        result = response.json()

        if result["success_feedback"]["success"]:
            props.token = result["token"]
        else:
            self.report({"ERROR"}, "Login failed :(")
        return {"FINISHED"}


class AuginReset(bpy.types.Operator):
    bl_idname = "bim.augin_reset"
    bl_label = "Upload Another Project"

    def execute(self, context):
        props = bpy.context.scene.AuginProperties
        props.is_success = False
        return {"FINISHED"}


class AuginCreateNewModel(bpy.types.Operator):
    bl_idname = "bim.augin_create_new_model"
    bl_label = "Create New Augin Model"

    def execute(self, context):
        import boto3
        from botocore.config import Config
        props = bpy.context.scene.AuginProperties

        # Create project
        url = "https://server.auge.pro.br/API/v3/augin_rest.php/new_model"

        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        props.project_filename = "BBM{}{}".format(
            datetime.datetime.now().strftime("%Y%m%d%H%M%S"), "".join(random.choice(chars) for _ in range(6))
        )
        addon_version = ".".join(
            [
                str(x)
                for x in [
                    addon.bl_info.get("version", (-1, -1, -1))
                    for addon in addon_utils.modules()
                    if addon.bl_info["name"] == "BlenderBIM"
                ][0]
            ]
        )

        payload = {
            "user_token": props.token,
            "partner_token": "Mmf2zpxdgrkHaUNRm6Cv7GLJdBAeb7Rn",
            "project_name": props.project_name,
            "model_filename": props.project_filename + ".ifc",
            "thumb_filename": props.project_filename + ".png",
            "app_name": "BlenderBIM",
            "sw_version": bpy.app.version_string,
            "plugin_version": addon_version,
        }
        response = requests.request("POST", url, data=payload)
        result = response.json()

        # Upload to S3
        my_config = Config(
            region_name=result["s3_region"],
        )

        client = boto3.client(
            "s3",
            aws_access_key_id=result["s3_key"],
            aws_secret_access_key=result["s3_secret"],
            aws_session_token=result["s3_token"],
            config=my_config,
        )

        # Generate thumb
        old_file_format = context.scene.render.image_settings.file_format
        old_filepath = context.scene.render.filepath

        cam = bpy.data.cameras.new("Camera")
        cam_obj = bpy.data.objects.new("Camera", cam)
        context.scene.collection.objects.link(cam_obj)
        context.scene.camera = cam_obj

        tmpdir = tempfile.mkdtemp()
        thumb_path = os.path.join(tmpdir, "thumb.png")
        context.scene.render.image_settings.file_format = "PNG"
        context.scene.render.filepath = thumb_path
        bpy.ops.render.opengl(write_still=True)

        context.scene.render.image_settings.file_format = old_file_format
        context.scene.render.filepath = old_filepath

        client.upload_file(bpy.context.scene.BIMProperties.ifc_file, result["s3_bucket"], result["model_path"])
        client.upload_file(thumb_path, result["s3_bucket"], result["thumb_path"])


        # Notify done
        url = "https://server.auge.pro.br/API/v3/augin_rest.php/files_uploaded"
        payload = {
            "user_token": props.token,
            "ifc_filesize": os.path.getsize(bpy.context.scene.BIMProperties.ifc_file),
            "model_filesize": os.path.getsize(bpy.context.scene.BIMProperties.ifc_file),
            "thumb_filesize": os.path.getsize(thumb_path),
            "model_upload_path": result["model_path"],
            "thumb_upload_path": result["thumb_path"],
            "model_id": result["model_id"],
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, headers=headers, data=payload)

        shutil.rmtree(tmpdir)
        props.is_success = True
        return {"FINISHED"}
