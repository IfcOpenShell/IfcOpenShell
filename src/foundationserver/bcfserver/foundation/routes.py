from flask.blueprints import Blueprint
from flask import render_template, redirect, url_for, flash, request
from werkzeug import datastructures
from .forms import RegisterForm, LoginForm, OauthForm
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, OAuth2Client, OAuth2AuthorizationCode, OAuth2Token
import base64
from werkzeug.security import gen_salt
import time
import urllib
import json
from run import db, app

foundation_obj = Blueprint(
    "foundation_obj",
    __name__,
    template_folder="templates",
)


def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


@foundation_obj.route("/")
def homepage():
    return render_template("index.html")
    # return "homepage"


@foundation_obj.route("/register", methods=["GET", "POST"])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data,
        )

        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(
            f"Account created successfully! {user_to_create.username}",
            category="success",
        )
        return redirect(url_for("foundation_obj.homepage"))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(
                f"There was an error with creating a user: {err_msg}", category="danger"
            )

    return render_template("register.html", form=form)


@foundation_obj.route("/createclient", methods=["GET", "POST"])
@login_required
def create_client():
    grants = [
        "AuthorizationCodeGrant",
        "ImplicitGrant",
        "ResourceOwnerPasswordCredentialsGrant",
        "ClientCredentialsGrant",
        "RefreshTokenGrant",
    ]
    form = OauthForm()
    if form.validate_on_submit():
        client_id = gen_salt(24)
        client_id_issued_at = int(time.time())

        client = OAuth2Client(
            client_id=client_id,
            client_id_issued_at=client_id_issued_at,
            user_id=current_user.id,
        )
        client_metadata = {
            "client_name": form.client_name.data,
            "grant_types": split_by_crlf(form.grant_types.data),
            "response_types": split_by_crlf(form.response_types.data),
            "scope": form.scope.data,
            "token_endpoint_auth_method": "client_secret_basic",
        }
        client.client_secret = gen_salt(48)

        client.set_client_metadata(client_metadata)
        db.session.add(client)
        db.session.commit()
        flash(
            "Oauth Client Created Successfully",
            category="info",
        )
        clients = OAuth2Client.query.filter_by(user_id=current_user.id).all()
        for client in clients:
            print(client.client_info)
            print(client.client_metadata)
        return render_template("clientdata.html", user=current_user.id, clients=clients)
    return render_template("createclient.html", form=form, grants=grants)


@foundation_obj.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            return redirect(url_for("foundation_obj.homepage"))
        else:
            flash(
                "Invalid Credentials",
                category="danger",
            )

    return render_template("login.html", form=form)


@foundation_obj.route("/logout")
def logoutpage():
    logout_user()
    flash("You have been logged out!", category="info")
    return redirect(url_for("foundation_obj.homepage"))


@foundation_obj.route("/foundation/1.0/auth")
def foundation_auth():
    data = {
        "oauth2_auth_url": "http://127.0.0.1:5000/oauth/authorize",
        "oauth2_token_url": "http://127.0.0.1:5000/oauth/token",
        "supported_oauth2_flows": ["authorization_code"],
    }
    response = app.response_class(
        response=json.dumps(data), status=200, mimetype="application/json"
    )
    return response


@foundation_obj.route("/foundation/versions")
def foundation_versions():
    Body = {
        "versions": [
            {
                "api_id": "opencde-foundation",
                "version_id": "1.0",
                "detailed_version": "https://github.com/BuildingSMART/opencde-foundation-API/tree/v1.0",
            },
            # {
            #     "api_id": "bcf",
            #     "version_id": "2.1",
            #     "detailed_version": "https://github.com/buildingSMART/BCF-API/tree/release_2_1",
            #     "api_base_url": "http://127.0.0.1:5000/bcf/2.1"
            # },
            {
                "api_id": "bcf",
                "version_id": "3.0",
                "detailed_version": "https://github.com/buildingSMART/BCF-API/tree/release_3_0",
                "api_base_url": "http://127.0.0.1:5000/bcf/3.0",
            },
        ]
    }
    response = app.response_class(
        response=json.dumps(Body), status=200, mimetype="application/json"
    )
    return response


@foundation_obj.route("/outh/login", methods=["GET", "POST"])
def oauth_login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(
                "Invalid Credentials",
                category="info",
            )
            client_id = request.args.get("client_id")
            redirect_uri = request.args.get("redirect_uri")
            state = request.args.get("state")
            return redirect(
                url_for(
                    "foundation_obj.authorize",
                    client_id=client_id,
                    redirect_uri=redirect_uri,
                    state=state,
                )
            )
        else:
            flash(
                "Invalid Credentials",
                category="danger",
            )
    return render_template("ologin.html", form=form)


@foundation_obj.route("/oauth/authorize", methods=["GET", "POST"])
def authorize():
    client_id = request.args.get("client_id")
    redirect_uri = request.args.get("redirect_uri")
    state = request.args.get("state")
    if current_user.is_anonymous:
        flash("Please Login !", category="info")
        query = request.query_string
        return redirect(
            url_for(
                "foundation_obj.oauth_login",
                client_id=client_id,
                redirect_uri=redirect_uri,
                state=state,
            )
        )
    else:
        try:

            user = current_user.id
            flash(message=redirect_uri, category="warning")
            client = OAuth2Client.query.filter_by(client_id=client_id).first()
            if client:
                if client.user_id == user:
                    code = gen_salt(48)
                    OauthCode = OAuth2AuthorizationCode(
                        client_id=client_id,
                        redirect_uri=redirect_uri,
                        user_id=user,
                        code=code,
                        response_type="code",
                    )
                    db.session.add(OauthCode)
                    db.session.commit()
                    query = urllib.parse.urlencode(
                        {
                            "code": OauthCode.code,
                            "state": state,
                        }
                    )
                    return redirect(f"{redirect_uri}?{query}")
                else:
                    flash(
                        "You are not authorized to access this client",
                        category="danger",
                    )
            else:
                flash("Client not found", category="danger")
        except Exception as e:
            flash(e, category="danger")
    return render_template("oauth.html")


@foundation_obj.route("/oauth/token", methods=["POST"])
def issue_token():
    try:
        code = request.form["code"]
        Headers = str.split(request.headers["Authorization"])
        decode_header = base64.b64decode(Headers[1]).decode("utf-8")
        creds = decode_header.split(":")
        client_id = creds[0]
        # print(code, Headers, decode_header, creds, client_id)
        auth_code = OAuth2AuthorizationCode.query.filter_by(code=code).first()
        if auth_code:
            if auth_code.client_id == client_id:
                access_token = gen_salt(48)
                refresh_token = gen_salt(48)
                expires_in = 3600
                OauthToken = OAuth2Token(
                    client_id=auth_code.client_id,
                    user_id=auth_code.user_id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_in=expires_in,
                    scope=auth_code.scope,
                    token_type="Bearer",
                )
                db.session.add(OauthToken)
                db.session.commit()
                query = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": expires_in,
                }
                response = app.response_class(
                    response=json.dumps(query),
                    status=200,
                    mimetype="application/json",
                )
                print(query)
                return response
            else:
                flash(
                    "You are not authorized to access this client",
                    category="danger",
                )
        else:
            flash("Client not found", category="danger")
    except Exception as e:
        flash(e, category="danger")
    return render_template("oauth.html")
