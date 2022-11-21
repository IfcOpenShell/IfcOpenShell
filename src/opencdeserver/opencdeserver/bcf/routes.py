
# OpenCDE - OpenCDE Python implementation
# Copyright (C) 2021 Prabhat Singh <singh01prabhat@gmail.com>
#
# This file is part of OpenCDE.
#
# OpenCDE is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenCDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with OpenCDE.  If not, see <http://www.gnu.org/licenses/>.

from flask import jsonify, url_for, redirect, render_template, request, session, send_file
from flask_login import login_user, logout_user, login_required, current_user
from flask.blueprints import Blueprint
from foundation.models import User, OAuth2AuthorizationCode, OAuth2Token, OAuth2Client
from run import app, db
import json
import os
from flask_expects_json import expects_json

bcf = Blueprint("bcf", __name__, template_folder="templates", url_prefix="/bcf/3.0")
my_absolute_dirpath = os.path.abspath(os.path.dirname(__file__))
data = open(
    f"{my_absolute_dirpath}/project.json",
)
jdata = json.load(data)
schema_path = os.path.join(my_absolute_dirpath, "schemas")


def validate_client(request):
    Headers = str.split(request.headers["Authorization"])
    token = Headers[1]
    access_token = OAuth2Token.query.filter_by(access_token=token).first()
    if access_token:
        return True
    else:
        return False


def invalid_user():
    response = jsonify({"message": "User not recognized"})
    response.status = 401
    return response


def invalid_project():
    response = jsonify({"message": "Project not found"})
    response.status_code = 404
    return response


@bcf.route("/projects")
def projects():
    if validate_client(request):
        return jsonify(jdata["Projects"])
    return invalid_user()


@bcf.route("/")
@login_required
def bcf_3():
    return "<h1>BCF  HOMPAGE</h1>"


@bcf.route("/projects/<project_id>")
def project_details(project_id):
    if validate_client(request):
        for project in jdata["Projects"]:
            if project["project_id"] == project_id:
                return jsonify(project)
        return invalid_project()
    return invalid_user()


project_put = open(f"{schema_path}/Project/project_PUT.json")
project_put = json.load(project_put)


@bcf.route("/projects/<project_id>", methods=["PUT"])
@expects_json(project_put)
def update_project(project_id):
    if validate_client(request) and request.method == "PUT":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                response = jsonify(data)
                return response
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/extensions")
def extensions(project_id):
    if validate_client(request):
        for project in jdata["Projects"]:
            if project["project_id"] == project_id:
                return jsonify(jdata["Extensions"])
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics")
def topics(project_id):

    if validate_client(request):
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                return jsonify(jdata["Topics"])
        return invalid_project()
    return invalid_user()


topic_post = open(f"{schema_path}/Collaboration/Topic/topic_POST.json")
topic_post = json.load(topic_post)


@bcf.route("/projects/<project_id>/topics/<topic_id>", methods=["POST"])
@expects_json(topic_post)
def create_topic(project_id, topic_id):
    if validate_client(request) and request.method == "POST":
        body = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        response = jsonify(body)
                        response.status_code = 201
                        return response
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>")
def topic_details(project_id, topic_id):
    if validate_client(request):
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify(topic)
        return invalid_project()
    return invalid_user()


topic_put = open(f"{schema_path}/Collaboration/Topic/topic_PUT.json")
topic_put = json.load(topic_put)


@bcf.route("/projects/<project_id>/topics/<topic_id>", methods=["PUT"])
@expects_json(topic_put)
def update_topic(project_id, topic_id):
    if validate_client(request) and request.method == "PUT":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify(data)
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>", methods=["DELETE"])
def delete_topic(project_id, topic_id):
    if validate_client(request) and request.method == "DELETE":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify("OK")
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/snippet", methods=["GET"])
def get_snippet(project_id, topic_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return send_file(f"{my_absolute_dirpath}/success.txt", download_name="snippet.txt")
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/snippet", methods=["PUT"])
def update_snippet(project_id, topic_id):
    if validate_client(request) and request.method == "PUT":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify("PUT Request Successful")
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/files_information", methods=["GET"])
def get_files_information(project_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                return jsonify(jdata["Files"])
        return invalid_project()
    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/files", methods=["GET"])
def get_files(project_id, topic_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify("Get request for files successful")
        return invalid_project()
    return invalid_user()


file_put = open(f"{schema_path}/Collaboration/File/file_PUT.json")
file_put = json.load(file_put)


@bcf.route("/projects/<project_id>/topics/<topic_id>/files", methods=["PUT"])
@expects_json(file_put)
def update_files(project_id, topic_id):
    if validate_client(request) and request.method == "PUT":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify(data)
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/comments", methods=["GET"])
def get_comments(project_id, topic_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify(jdata["Comments"])
        return invalid_project()
    return invalid_user()


comment_post = open(f"{schema_path}/Collaboration/Comment/comment_POST.json")
comment_post = json.load(comment_post)


@bcf.route("/projects/<project_id>/topics/<topic_id>/comments", methods=["POST"])
@expects_json(comment_post)
def create_comments(project_id, topic_id):
    if validate_client(request) and request.method == "POST":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        response = jsonify(data)
                        response.status_code = 201
                        return response
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/comments/<comment_id>", methods=["GET"])
def get_comment(project_id, topic_id, comment_id):

    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        for comment in jdata["Comments"]:
                            if (comment["guid"]) == comment_id:
                                return jsonify(comment)
        return invalid_project()
    return invalid_user()


comment_put = open(f"{schema_path}/Collaboration/Comment/comment_PUT.json")
comment_put = json.load(comment_put)


@bcf.route("/projects/<project_id>/topics/<topic_id>/comments/<comment_id>", methods=["PUT"])
@expects_json(comment_put)
def update_comment(project_id, topic_id, comment_id):
    if validate_client(request) and request.method == "PUT":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        for comment in jdata["Comments"]:
                            if (comment["guid"]) == comment_id:
                                return jsonify(data)
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/comments/<comment_id>", methods=["DELETE"])
def delete_comment(project_id, topic_id, comment_id):
    if validate_client(request) and request.method == "DELETE":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        for comment in jdata["Comments"]:
                            if (comment["guid"]) == comment_id:
                                return jsonify("OK")
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/viewpoints", methods=["GET"])
def get_viewpoints(project_id, topic_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if project["project_id"] == project_id:
                for topic in jdata["Topics"]:
                    if topic["guid"] == topic_id:
                        return jsonify(jdata["Viewpoints"])
        return invalid_project()
    return invalid_user()


viewpoint_post = open(f"{schema_path}/Collaboration/Viewpoint/viewpoint_POST.json")
viewpoint_post = json.load(viewpoint_post)


@bcf.route("/projects/<project_id>/topics/<topic_id>/viewpoints", methods=["POST"])
@expects_json(viewpoint_post)
def create_viewpoints(project_id, topic_id):
    if validate_client(request) and request.method == "POST":
        for project in jdata["Projects"]:
            if project["project_id"] == project_id:
                for topic in jdata["Topics"]:
                    if topic["guid"] == topic_id:
                        data = request.get_json()
                        response = jsonify(data)
                        response.status_code = 201
                        return response
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>", methods=["GET"])
def get_viewpoint(project_id, topic_id, viewpoint_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if project["project_id"] == project_id:
                for topic in jdata["Topics"]:
                    if topic["guid"] == topic_id:
                        for viewpoint in jdata["Viewpoints"]:
                            if viewpoint["guid"] == viewpoint_id:
                                response = jsonify(viewpoint)
                                response.status_code = 200
                                return response
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>", methods=["DELETE"])
def delete_viewpoint(project_id, topic_id, viewpoint_id):
    if validate_client(request) and request.method == "DELETE":
        for project in jdata["Projects"]:
            if project["project_id"] == project_id:
                for topic in jdata["Topics"]:
                    if topic["guid"] == topic_id:
                        for viewpoint in jdata["Viewpoints"]:
                            if viewpoint["guid"] == viewpoint_id:
                                response = jsonify(viewpoint)
                                response.status_code = 200
                                return response
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/snapshot", methods=["GET"])
def get_snapshot(project_id, topic_id, viewpoint_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if project["project_id"] == project_id:
                for topic in jdata["Topics"]:
                    if topic["guid"] == topic_id:
                        for viewpoint in jdata["Viewpoints"]:
                            if viewpoint["guid"] == viewpoint_id:
                                response = jsonify(viewpoint["snapshot"])
                                response.status_code = 200
                                return response
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/bitmaps/<bitmap_id>", methods=["GET"])
def get_bitmap(project_id, topic_id, viewpoint_id, bitmap_id):
    if validate_client(request):
        for project in jdata["Projects"]:
            if project["project_id"] == project_id:
                for topic in jdata["Topics"]:
                    if topic["guid"] == topic_id:
                        for viewpoint in jdata["Viewpoints"]:
                            if viewpoint["guid"] == viewpoint_id:
                                for bitmap in viewpoint["bitmaps"]:
                                    if bitmap["guid"] == bitmap_id:
                                        response = jsonify(bitmap)
                                        response.status_code = 200
                                        return response
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/selection", methods=["GET"])
def get_selection(project_id, topic_id, viewpoint_id):
    if validate_client(request):
        for project in jdata["Projects"]:
            if project["project_id"] == project_id:
                for topic in jdata["Topics"]:
                    if topic["guid"] == topic_id:
                        for viewpoint in jdata["Viewpoints"]:
                            if viewpoint["guid"] == viewpoint_id:
                                response = jsonify(viewpoint["selection"])
                                response.status_code = 200
                                return response
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/coloring", methods=["GET"])
def get_coloring(project_id, topic_id, viewpoint_id):
    if validate_client(request):
        for project in jdata["Projects"]:
            if project["project_id"] == project_id:
                for topic in jdata["Topics"]:
                    if topic["guid"] == topic_id:
                        for viewpoint in jdata["Viewpoints"]:
                            if viewpoint["guid"] == viewpoint_id:
                                response = jsonify(viewpoint["coloring"])
                                response.status_code = 200
                                return response
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/visibility", methods=["GET"])
def get_visibility(project_id, topic_id, viewpoint_id):
    if validate_client(request):
        for project in jdata["Projects"]:
            if project["project_id"] == project_id:
                for topic in jdata["Topics"]:
                    if topic["guid"] == topic_id:
                        for viewpoint in jdata["Viewpoints"]:
                            if viewpoint["guid"] == viewpoint_id:
                                response = jsonify(viewpoint["visibility"])
                                response.status_code = 200
                                return response
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/related_topics", methods=["GET"])
def get_related_topics(project_id, topic_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify(jdata["RelatedTopics"])
        return invalid_project()
    return invalid_user()


related_topics_put = open(f"{schema_path}/Collaboration/RelatedTopic/related_topic_PUT.json")
related_topics_put = json.load(related_topics_put)


@bcf.route("/projects/<project_id>/topics/<topic_id>/related_topics", methods=["PUT"])
@expects_json(related_topics_put)
def update_related_topics(project_id, topic_id):
    if validate_client(request) and request.method == "PUT":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify(data)
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/document_references", methods=["GET"])
def get_document_references(project_id, topic_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify(jdata["DocumentReferences"])
        return invalid_project()
    return invalid_user()


document_reference_post = open(f"{schema_path}/Collaboration/DocumentReference/document_reference_POST.json")
document_reference_post = json.load(document_reference_post)


@bcf.route("/projects/<project_id>/topics/<topic_id>/document_references", methods=["POST"])
@expects_json(document_reference_post)
def create_document_references(project_id, topic_id):
    if validate_client(request) and request.method == "POST":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        response = jsonify(data)
                        response.status_code = 201
                        return response
        return invalid_project()
    return invalid_user()


document_reference_put = open(f"{schema_path}/Collaboration/DocumentReference/document_reference_PUT.json")
document_reference_put = json.load(document_reference_put)


@bcf.route(
    "/projects/<project_id>/topics/<topic_id>/document_references/<document_reference_id>",
    methods=["PUT"],
)
@expects_json(document_reference_put)
def update_document_references(project_id, topic_id, document_reference_id):
    if validate_client(request) and request.method == "PUT":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        for document in jdata["DocumentReferences"]:
                            if (document["guid"]) == document_reference_id:
                                return jsonify(data)
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/documents", methods=["GET"])
def get_documents(project_id, topic_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify(jdata["Documents"])
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/documents", methods=["POST"])
def create_documents(project_id, topic_id):
    if validate_client(request) and request.method == "POST":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        response = jsonify(data)
                        response.status_code = 201
                        return response
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/documents/<document_id>", methods=["GET"])
def get_document(project_id, topic_id, document_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        for document in jdata["Documents"]:
                            if (document["guid"]) == document_id:
                                return send_file(f"{my_absolute_dirpath}/success.txt", download_name="document.txt")
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/events", methods=["GET"])
def get_events(project_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                return jsonify(jdata["Events"])
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/events", methods=["GET"])
def get_topic_events(project_id, topic_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        for event in jdata["Events"]:
                            if (event["topic_guid"]) == topic_id:
                                return jsonify(event)
        return invalid_project()
    return invalid_user()


@bcf.route("/projects/<project_id>/topics/comments/events", methods=["GET"])
def get_comments_events(project_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                return jsonify(jdata["EventComments"])
        return invalid_project()
    return invalid_user()


@bcf.route(
    "/projects/<project_id>/topics/<topic_id>/comments/<comment_id>/events",
    methods=["GET"],
)
def get_comment_events(project_id, topic_id, comment_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        for comment in jdata["EventComments"]:
                            if (comment["comment_guid"]) == comment_id:
                                return jsonify(comment)
        return invalid_project()
    return invalid_user()
