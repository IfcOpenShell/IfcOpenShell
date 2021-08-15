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
    response = jsonify({"error": "User not recognized"})
    response.status = 401
    return response


def invalid_project():
    response = jsonify({"message": "Project not found"})
    response.status = 404
    return response


@bcf.route("/projects")
def projects():
    return invalid_user()
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
    access_token = validate_client(request)
    if access_token and request.method == "PUT":
        data = request.form["data"]
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                response = app.response_class(
                    response=data,
                    status=200,
                    mimetype="application/json",
                )
                return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


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
    access_token = validate_client(request)
    if access_token:
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                response = app.response_class(
                    response=jdata["Topics"],
                    status=200,
                    mimetype="application/json",
                )
                return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>", methods=["POST"])
def create_topic(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "POST":
        body = request.form["data"]
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=body,
                            status=201,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>")
def topic_details(project_id, topic_id):
    access_token = validate_client(request)
    if access_token:
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=j,
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>", methods=["PUT"])
def update_topic(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "PUT":
        data = request.form["data"]
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=data,
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>", methods=["DELETE"])
def delete_topic(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "DELETE":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        message = {"DELETED"}
                        response = app.response_class(
                            response=json.dumps(message),
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>/snippet", methods=["GET"])
def get_snippet(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=json.dumps("Snippet test successfull"),
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>/snippet", methods=["PUT"])
def update_snippet(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "PUT":
        data = request.form["data"]
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=data,
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/files_information", methods=["GET"])
def get_files_information(project_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                response = app.response_class(
                    response=jdata["Files"],
                    status=200,
                    mimetype="application/json",
                )
                return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>/files", methods=["GET"])
def get_files(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=json.dumps("Get request for files successfull"),
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>/files", methods=["PUT"])
def update_files(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "PUT":
        data = request.form["data"]
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=data,
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>/comments", methods=["GET"])
def get_comments(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=jdata["Comments"],
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>/comments", methods=["POST"])
def create_comments(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "POST":
        data = request.form["data"]
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=data,
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route(
    "/projects/<project_id>/topics/<topic_id>/comments/<comment_id>", methods=["GET"]
)
def get_comment(project_id, topic_id, comment_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        for k in jdata["Comments"]:
                            if (k["guid"]) == comment_id:
                                response = app.response_class(
                                    response=k,
                                    status=200,
                                    mimetype="application/json",
                                )
                                return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route(
    "/projects/<project_id>/topics/<topic_id>/comments/<comment_id>", methods=["PUT"]
)
def update_comment(project_id, topic_id, comment_id):
    access_token = validate_client(request)
    if access_token and request.method == "PUT":
        data = request.form["data"]
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        for k in jdata["Comments"]:
                            if (k["guid"]) == comment_id:
                                response = app.response_class(
                                    response=data,
                                    status=200,
                                    mimetype="application/json",
                                )
                                return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route(
    "/projects/<project_id>/topics/<topic_id>/comments/<comment_id>", methods=["DELETE"]
)
def delete_comment(project_id, topic_id, comment_id):
    access_token = validate_client(request)
    if access_token and request.method == "DELETE":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        for k in jdata["Comments"]:
                            if (k["guid"]) == comment_id:
                                message = {"DELETED"}
                                response = app.response_class(
                                    response=json.dumps(message),
                                    status=200,
                                    mimetype="application/json",
                                )
                                return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


"""
***Add ViewPoints Routes Here ***
"""


@bcf.route("/projects/<project_id>/topics/<topic_id>/related_topics", methods=["GET"])
def get_related_topics(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=jdata["RelatedTopics"],
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>/related_topics", methods=["PUT"])
def update_related_topics(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "PUT":
        data = request.form["data"]
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=data,
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route(
    "/projects/<project_id>/topics/<topic_id>/document_references", methods=["GET"]
)
def get_document_references(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=jdata["DocumentReferences"],
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route(
    "/projects/<project_id>/topics/<topic_id>/document_references", methods=["POST"]
)
def create_document_references(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "POST":
        data = request.form["data"]
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=data,
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route(
    "/projects/<project_id>/topics/<topic_id>/document_references/<document_reference_id>",
    methods=["PUT"],
)
def update_document_references(project_id, topic_id, document_reference_id):
    access_token = validate_client(request)
    if access_token and request.method == "PUT":
        data = request.form["data"]
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        for k in jdata["DocumentReferences"]:
                            if (k["guid"]) == document_reference_id:
                                response = app.response_class(
                                    response=data,
                                    status=200,
                                    mimetype="application/json",
                                )
                                return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>/documents", methods=["GET"])
def get_documents(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=jdata["Documents"],
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>/documents", methods=["POST"])
def create_documents(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "POST":
        data = request.form["data"]
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        response = app.response_class(
                            response=data,
                            status=200,
                            mimetype="application/json",
                        )
                        return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route(
    "/projects/<project_id>/topics/<topic_id>/documents/<document_id>", methods=["GET"]
)
def get_document(project_id, topic_id, document_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        for k in jdata["Documents"]:
                            if (k["guid"]) == document_id:
                                response = app.response_class(
                                    response=k,
                                    status=200,
                                    mimetype="application/json",
                                )
                                return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/events", methods=["GET"])
def get_events(project_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                response = app.response_class(
                    response=jdata["Events"],
                    status=200,
                    mimetype="application/json",
                )
                return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/<topic_id>/events", methods=["GET"])
def get_topic_events(project_id, topic_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        for k in jdata["Events"]:
                            if (k["topic_guid"]) == topic_id:
                                response = app.response_class(
                                    response=k,
                                    status=200,
                                    mimetype="application/json",
                                )
                                return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route("/projects/<project_id>/topics/comments/events", methods=["GET"])
def get_comments_events(project_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    response = app.response_class(
                        response=jdata["EventComments"],
                        status=200,
                        mimetype="application/json",
                    )
                    return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response


@bcf.route(
    "/projects/<project_id>/topics/<topic_id>/comments/<comment_id>/events",
    methods=["GET"],
)
def get_comment_events(project_id, topic_id, comment_id):
    access_token = validate_client(request)
    if access_token and request.method == "GET":
        for i in jdata["Projects"]:
            if (i["project_id"]) == project_id:
                for j in jdata["Topics"]:
                    if (j["guid"]) == topic_id:
                        for k in jdata["EventComments"]:
                            if (k["comment_guid"]) == comment_id:
                                response = app.response_class(
                                    response=k,
                                    status=200,
                                    mimetype="application/json",
                                )
                                return response
        response = invalid_project()
        return response
    else:
        response = invalid_user()
        return response
