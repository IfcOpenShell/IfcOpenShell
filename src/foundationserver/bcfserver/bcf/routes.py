from operator import methodcaller
from flask import jsonify, url_for, redirect, render_template, request, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask.blueprints import Blueprint
from foundation.models import User, OAuth2AuthorizationCode, OAuth2Token, OAuth2Client
from run import app, db
import json
import os

bcf = Blueprint("bcf", __name__, template_folder="templates", url_prefix="/bcf/3.0")
my_absolute_dirpath = os.path.abspath(os.path.dirname(__file__))
data = open(
    f"{my_absolute_dirpath}/project.json",
)
jdata = json.load(data)


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


@bcf.route("/projects/<project_id>", methods=["PUT"])
def update_project(project_id):
    if validate_client(request) and request.method == "PUT":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                response = jsonify(data)
                return response
        return invalid_project()
    else:
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

    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>", methods=["POST"])
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

    else:
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
    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>", methods=["PUT"])
def update_topic(project_id, topic_id):
    if validate_client(request) and request.method == "PUT":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify(data)
        return invalid_project()
    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>", methods=["DELETE"])
def delete_topic(project_id, topic_id):
    if validate_client(request) and request.method == "DELETE":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify({"OK"})
        return invalid_project()
    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/snippet", methods=["GET"])
def get_snippet(project_id, topic_id):
    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify({"Get Snippet Executed successfully"})
        return invalid_project()
    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/snippet", methods=["PUT"])
def update_snippet(project_id, topic_id):
    if validate_client(request) and request.method == "PUT":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify(data)
        return invalid_project()
    else:
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
                        return jsonify("Get request for files successfull")
        return invalid_project()

    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/files", methods=["PUT"])
def update_files(project_id, topic_id):

    if validate_client(request) and request.method == "PUT":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify(data)
        return invalid_project()

    else:
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
    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/comments", methods=["POST"])
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
    else:
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
    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/comments/<comment_id>", methods=["PUT"])
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
    else:
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

    else:
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
    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/viewpoints", methods=["POST"])
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
    else:
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
    else:
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
    else:
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
    else:
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
    else:
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
    else:
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
    else:
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
    else:
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
        return response
    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/related_topics", methods=["PUT"])
def update_related_topics(project_id, topic_id):

    if validate_client(request) and request.method == "PUT":
        data = request.get_json()
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                for topic in jdata["Topics"]:
                    if (topic["guid"]) == topic_id:
                        return jsonify(data)
        return invalid_project()

    else:
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

    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/<topic_id>/document_references", methods=["POST"])
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

    else:
        return invalid_user()


@bcf.route(
    "/projects/<project_id>/topics/<topic_id>/document_references/<document_reference_id>",
    methods=["PUT"],
)
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

    else:
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

    else:
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

    else:
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
                                return jsonify(document)
        return invalid_project()

    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/events", methods=["GET"])
def get_events(project_id):

    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                return jsonify(jdata["Events"])
        return invalid_project()

    else:
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

    else:
        return invalid_user()


@bcf.route("/projects/<project_id>/topics/comments/events", methods=["GET"])
def get_comments_events(project_id):

    if validate_client(request) and request.method == "GET":
        for project in jdata["Projects"]:
            if (project["project_id"]) == project_id:
                return jsonify(jdata["EventComments"])
        return invalid_project()

    else:
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

    else:
        return invalid_user()
