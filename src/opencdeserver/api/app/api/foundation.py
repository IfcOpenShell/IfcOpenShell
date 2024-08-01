import os

from typing import Optional

from fastapi import APIRouter, Request, Form
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models.request import *

from repository.foundation import foundation_db
from security.secure import authenticate_user, get_current_active_user

from uuid import uuid4
from api.logging import LoggingRoute
from security.secure import get_secrets

secrets = get_secrets()

router = APIRouter(route_class=LoggingRoute)

http_basic = HTTPBasic()
oauth2_state = None
authorization_code = None

templates = Jinja2Templates(directory="templates")

clients = {
    os.environ["KONTROLL_CLIENT_ID"]: {
        "name": os.environ["KONTROLL_CLIENT_NAME"],
        "secret": secrets["kontroll_client_secret"],
    }
}

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
#
#
# Foundations API

# 2.1 Versions Service
# GET /foundation/versions
#
# The Versions service is used to discover the available OpenCDE APIs
# and where to find them. The api_base_url field specifies the base path for each API.
#
# To clarify, the versions service allows specifying api_base_url for the Foundation API. However, to ensure
# discoverability, the Versions service is always served from the /foundation/versions base path regardless of the
# api_base_url parameter value.
#
# PARAMETER 	    TYPE 	DESCRIPTION 	                                        REQUIRED
# api_id 	        string 	Identifier of the API 	                                true
# version_id 	    string 	Identifier of the version 	                            true
# detailed_version 	string 	URL of the specification on GitHub 	                    false
# api_base_url 	    string 	Optional, fqURL, to allow servers to relocate the API   false


@router.get("/foundation/versions", tags=["api_versions_get"])
def api_versions_get():
    return {
        "versions": [
            {
                "api_id": "foundation",
                "version_id": "1.0",
                "detailed_version": "https://github.com/BuildingSMART/foundation-API/tree/release_1_0",
            },
            {
                "api_id": "bcf",
                "version_id": "3.0",
                "detailed_version": "https://github.com/buildingSMART/BCF-API/tree/release_3_0",
                "api_base_url": os.environ["KONTROLL_BASE_URL"] + "bcf/3.0",
            },
            {
                "api_id": "documents",
                "version_id": "1.0",
                "detailed_version": "https://github.com/buildingSMART/documents-API/tree/release_1_0",
                "api_base_url": os.environ["KONTROLL_BASE_URL"] + "documents/1.0",
            },
        ]
    }


# 2.2.1 Obtaining authentication information
# GET /foundation/1.0/auth
#
# PARAMETER 	                TYPE 	    DESCRIPTION 	                                        Required
# oauth2_auth_url 	            string 	    URL to authorization page  	                            false
# oauth2_token_url 	            string 	    URL for token requests 	                                false
# oauth2_dynamic_client_reg_url string 	    URL for automated client registration 	                false
# http_basic_supported 	        boolean 	Indicates if Http Basic Authentication is supported 	false
# supported_oauth2_flows 	    string[] 	array of supported OAuth2 flows 	                    true
#
# Requirement: oauth2_auth_url and oauth2_token_url must be present at the same time.
#
# "oauth2_dynamic_client_reg_url" is commented out since registration is not allowed.
# If properties are not present in the response, clients should assume that the functionality
# is not supported by the server.


@router.get("/foundation/1.0/auth", tags=["foundation_auth_get"])
def authentication_get():

    return_variable = {
        "oauth2_auth_url": os.environ["KONTROLL_BASE_URL"] + "foundation/oauth2/auth",
        "oauth2_token_url": os.environ["KONTROLL_BASE_URL"] + "foundation/oauth2/token",
        # "oauth2_dynamic_client_reg_url": os.environ['KONTROLL_BASE_URL'] + "foundation/oauth2/reg",
        "http_basic_supported": True,
        "supported_oauth2_flows": ["authorization_code_grant"],
    }
    print(return_variable)
    return return_variable


# Authentication url
# GET /foundation/oauth2/auth
#
# To initiate the workflow, the client sends the user to the "oauth2_auth_url" with the following parameters added:
#
# PARAMETER 	                VALUE
# response_type 	            code - as string literal
# client_id 	                your client id
# state 	                    unique user defined value
# scope                         defines the scope of access
# redirect_uri              	The redirect_uri registered for your client. This parameter is optional for
#                               OAUTH servers that don't support multiple redirect URLs
#
# EXAMPLE
# GET https://api.kontroll.digital/foundation/oauth2/auth?
# response_type=code
# &client_id=<your_client_id>
# &state=<user_defined_string>
# &scope=<some_number>
# &redirect_uri=http://localhost:10445/Callback


@router.get("/foundation/oauth2/auth", response_class=HTMLResponse)
def authorization(
    request: Request,
    response_type: str,
    client_id: str,
    state: str,
    scope: str,
    redirect_uri: str,
):

    client_name = clients[client_id]["name"]

    print(
        f"Response type: {response_type}, "
        f"Client_id: {client_id}, "
        f"Client_name: {client_name}, "
        f"State: {state}, "
        f"Scope: {scope},"
        f"Redirect_URI: {redirect_uri}."
    )

    # 3. Solibri sends the user to oauth2_auth_url with the following parameters:
    #   response_type=code, client_id=solibri_test_001, state=..., redirect_uri=uri, scope=...
    # 4. The API will ask the user to sign in with username and password.

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "response_type": response_type,
            "client_id": client_id,
            "client_name": client_name,
            "state": state,
            "scope": scope,
            "redirect_uri": redirect_uri,
        },
    )


@router.get("/foundation/oauth2/code")
def code(
    username: str,
    password: str,
    response_type: str,
    client_id,
    client_name,
    state: str,
    redirect_uri: str,
    scope: str = "",
):

    global oauth2_state
    oauth2_state = state

    print("Username: " + username + ". Password: " + password)
    user = authenticate_user(username, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # The user is signed in, now the main purpose of this function is to generate the authorization code.
    # There are many ways to generate this code, in our app it is simple the word "test".
    # Conventionally auth_code needs to be encrypted because it can contain credentials, scope
    # and other request related details.

    # This functions adds the authorization code to the user node in the graph.
    # The authorization code node self-destructs after time delay SECURITY_AUTHORIZATION_CODE_EXPIRE_SECONDS

    global authorization_code
    new_authorization_code = str(uuid4())

    if foundation_db.create_authorization_code(username, new_authorization_code, scope):
        authorization_code = new_authorization_code
        print(f"Authorization code: {authorization_code}")

    # 5. When the access code is returned, the server redirects the user to redirect_uri.
    #   http://localhost:10445/Callback&scope=test&code=xxx&state=xxx
    # 6. The code-parameter will be appended to the redirect_uri as a query parameter
    #   this code-parameter is the access code
    # 7. The state-parameter should also be appended to the redirect_uri as a query parameter
    # 8. If the user denies client access redirect_uri will instead contain an error query parameter
    return authorization_code


# /foundation/oauth2/reg is not in use, since registration is not allowed.

# Path to obtain token
# With the obtained authorization code,
# the client is able to request an access token from the server.
# The "oauth2_token_url" from the authentication resource
# is used to send token requests to, for example:
#
# Will return
# access_token 	    string 	    The issued OAuth2 token
# token_type 	    string 	    Always bearer
# expires_in 	    integer 	The lifetime of the access token in seconds
# refresh_token 	string  	The issued OAuth2 refresh token, one-time-usable only
#
# The POST request should be done via HTTP Basic Authorization
# with your application client_id as the username
# and your client_secret as the password
#
# username: client_id
# password: client_secret
#
# example
# POST https://example.com/foundation/oauth2/token?grant_type=authorization_code&code=<your_authorization_code>


@router.post("/foundation/oauth2/token", tags=["login_for_access_token_post"], status_code=201)
def login_for_access_token(
    grant_type: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    code: Optional[str] = Form(None),
    credentials: HTTPBasicCredentials = Depends(http_basic),
):

    print("grant_type: ", grant_type)
    print("refresh_token: ", refresh_token)
    print("code: ", code)
    print("credentials: ", credentials)

    # The API should check that the credentials (client_id and client_secret) are correct
    # credentials.username contains the client_id
    # credentials.password contains the client_secret
    if credentials.username not in clients or credentials.password != clients[credentials.username]["secret"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect client_id or client_secret",
        )

    if grant_type == "authorization_code":
        # use authorization code,
        # create access token and refresh token,
        # delete authorization code
        user_info = foundation_db.use_authorization_code(code)

    elif grant_type == "refresh_token":
        # use refresh token to get access token
        # delete old access token and old refresh token
        # create new access token and a new refresh token
        # return old access token and new refresh token
        user_info = foundation_db.use_refresh_token(refresh_token)

    user_info.token_type = "Bearer"
    user_info.expires_in = int(os.environ["SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS"])
    print("user_info: ", user_info)
    return user_info


# 3.1.1 Get current user
# GET /foundation/1.0/current-user
#
# Response body
# {
#     "id": "Architect@example.com",
#     "name": "John Doe"
# }


@router.get("/foundation/1.0/current-user", response_model=User, tags=["current_user_get"])
async def current_user_get(current_user: User = Depends(get_current_active_user)):
    return current_user
