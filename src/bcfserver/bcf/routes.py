from flask import jsonify, url_for, redirect, render_template, request, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask.blueprints import Blueprint

bcf = Blueprint("bcf", __name__, template_folder="templates", url_prefix="/bcf/3.0")


@bcf.route("/projects")
@login_required
def projects():
    # Body = {
    #     "project_id": "F445F4F2-4D02-4B2A-B612-5E456BEF9137",
    #     "name": "Example project 1",
    #     "authorization": {"project_actions": ["createTopic", "createDocument"]},
    # }, {
    #     "project_id": "A233FBB2-3A3B-EFF4-C123-DE22ABC8414",
    #     "name": "Example project 2",
    #     "authorization": {"project_actions": []},
    # }
    # return jsonify({"projects": Body})
    return "<h1>BCF PAGE</h1>"


@bcf.route("/")
@login_required
def bcf_3():
    return "<h1>BCF  HOMPAGE</h1>"


@bcf.route("/projects/<project_id>")
def project_details(project_id):
    return "Project details"
