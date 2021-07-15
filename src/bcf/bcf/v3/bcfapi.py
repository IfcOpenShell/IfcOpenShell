import uuid
import time
import json
import urllib
import requests
import webbrowser
import http.server
import base64


client_id, client_secret = "", ""


class OAuthReceiver(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        self.server.auth_code = query.get("code", [""])[0]
        self.server.auth_state = query.get("state", [""])[0]
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("You have now authenticated :) You may now close this browser window.".encode("utf-8"))


class Client:
    def __init__(self, client_id, client_secret):
        self.baseurl = None
        self.access_token = ""
        self.refresh_token = ""
        self.access_token_expires_on = time.time()
        self.refresh_token_expires_on = float("inf")
        self.auth_endpoint = None
        self.token_endpoint = None
        self.client_id = client_id
        self.client_secret = client_secret
        self.version_ids = {}
        self.version = None
        self.auth_method = None
        self.redirect_uri = None
        self.api_baseurl = None

    def get(self, endpoint, params=None, is_auth_required=False):
        headers = {"Authorization": "Bearer " + self.get_access_token()}
        return requests.get(f"{self.api_baseurl}{endpoint}", headers=headers, params=params or None).json()

    def post(self, endpoint, data=None, params=None):
        headers = {
            "Authorization": "Bearer " + self.get_access_token(),
            "Content-type": "application/json",
        }
        resp = requests.post(
            f"{self.api_baseurl}{endpoint}",
            headers=headers,
            params=params or None,
            data=data or None,
        )
        return resp.status_code, resp.text

    def put(self, endpoint, data=None, params=None):
        headers = {
            "Authorization": "Bearer " + self.get_access_token(),
            "Content-type": "application/json",
        }
        resp = requests.put(
            f"{self.baseurl}{endpoint}",
            headers=headers,
            params=params or None,
            data=data or None,
        )
        return resp.status_code, resp.text

    def set_urls(self, base_url=None, redirect_uri=None):
        self.baseurl = base_url
        self.redirect_uri = redirect_uri

    def delete(self, endpoint, params=None):
        headers = {"Authorization": "Bearer " + self.get_access_token()}
        resp = requests.put(
            f"{self.baseurl}{endpoint}",
            headers=headers,
            params=params or None,
        )
        return resp.status_code

    def get_access_token(self):
        if self.access_token and self.access_token_expires_on > time.time():
            return self.access_token
        elif self.refresh_token and self.refresh_token_expires_on > time.time():
            self.get_refresh_token()
        else:
            self.login()
        return self.access_token

    def get_auth_methods(self):
        resp = requests.get(f"{self.baseurl}opencde/1.0/auth")
        return resp.json()["supported_oauth2_flows"]

    def get_versions(self):
        resp = requests.get(f"{self.baseurl}opencde/versions")
        resp_values = resp.json()["versions"]
        for version in resp_values:
            if "api_base_url" in version:
                self.version_ids.update({version["version_id"]: version["api_base_url"]})
        return self.version_ids

    def set_version(self, version=None):
        self.version = version
        self.api_baseurl = self.version_ids[self.version]

    def login(self):
        resp = requests.get(f"{self.baseurl}opencde/1.0/auth")
        values = resp.json()
        self.auth_endpoint = values["oauth2_auth_url"]
        self.token_endpoint = values["oauth2_token_url"]

        with http.server.HTTPServer(("", 8080), OAuthReceiver) as server:
            state = str(uuid.uuid4())
            query = urllib.parse.urlencode(
                {
                    "client_id": self.client_id,
                    "response_type": "code",
                    "state": state,
                    "redirect_uri": f"http://localhost:{server.server_address[1]}/{self.redirect_uri}",
                }
            )
            if "?" in self.auth_endpoint:
                webbrowser.open(f"{self.auth_endpoint}&{query}")
            else:
                webbrowser.open(f"{self.auth_endpoint}?{query}")
            server.timeout = 100
            server.state = state
            server.handle_request()
            if server.auth_code and server.auth_state == state:
                data = {
                    "grant_type": "authorization_code",
                    "code": server.auth_code,
                    "redirect_uri": f"http://localhost:{server.server_address[1]}/{self.redirect_uri}",
                }
                auth_string = f"{self.client_id}:{self.client_secret}"
                header_string = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
                headers = {"Authorization": f"Basic {header_string}"}
                self.set_tokens_from_response(requests.post(self.token_endpoint, data=data, headers=headers))

    def get_refresh_token(self):
        self.set_tokens_from_response(
            requests.post(
                self.token_endpoint,
                params={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
            ).json()
        )

    def get_new_access_token(self):
        auth_string = f"{self.client_id}:{self.client_secret}"
        header_string = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
        headers = {"Authorization": f"Basic {header_string}"}
        self.set_tokens_from_response(
            requests.post(
                self.token_endpoint,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
                headers=headers,
            ).json()
        )

    def set_auth_method(self, method="authorization_code_grant"):
        if method != "authorization_code_grant":
            raise NotImplementedError(f"{method} not supported")
        else:
            self.auth_method = method

    def set_tokens_from_response(self, response):
        response = response.json()
        self.access_token = response["access_token"]
        self.refresh_token = response["refresh_token"]
        self.access_token_expires_on = time.time() + response["expires_in"]
        if "refresh_token_expires_in" in response:
            self.refresh_token_expires_on = time.time() + response["refresh_token_expires_in"]

    def get_projects(self) -> list:
        return self.get(
            f"/projects",
        )

    def get_project(
        self,
        project_id="",
    ) -> dict:
        return self.get(
            f"/projects/{project_id}",
            {
                "project_id": project_id,
            },
        )

    def update_project(self, project_id="", data=None) -> dict:
        url = f"{self.baseurl}/projects/{project_id}"
        headers = {"Authorization": "Bearer " + self.get_access_token()}
        resp = requests.put(url, headers=headers, data=data)
        return resp.status_code, resp.text

    def get_extensions(
        self,
        project_id="",
    ) -> dict:
        return self.get(
            f"/projects/{project_id}/extensions",
            {
                "project_id": project_id,
            },
        )

    def get_topics(
        self,
        project_id="",
        topics="",
        query_string=None,
    ) -> list:
        # return self.get(
        #     f"/projects/{project_id}/topics",
        #     {
        #         "project_id": project_id,
        #         "topics": topics,
        #         "query_string": query_string,
        #     },
        # )
        pass

    def get_topic(self, project_id="", topic_id="") -> dict:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def create_topic(self, project_id="", data=None):
        return self.post(f"/projects/{project_id}/topics", data=data)

    def update_topic(self, project_id="", topic_id="", data=None) -> dict:
        return self.put(f"/projects/{project_id}/topics/{topic_id}", data=data)

    def delete_topic(self, project_id="", topic_id=""):
        return self.delete(f"/projects/{project_id}/topics/{topic_id}")

    def get_snippet(self, project_id="", topic_id="") -> str:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/snippet",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def update_snippet(self, project_id="", topic_id="", data=None):
        return self.put(f"/projects/{project_id}/topics", data=data)

    def get_files_information(self, project_id="") -> list:
        return self.get(
            f"/projects/{project_id}/files_information",
            {
                "project_id": project_id,
            },
        )

    def get_files(self, project_id="", topic_id="") -> list:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/files",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def update_files(
        self,
        project_id="",
        topic_id="",
        data=None,
        params=None,
    ):
        return self.put(
            f"/projects/{project_id}/topics/{topic_id}/files",
            data=data,
        )

    def get_comments(self, project_id="", topic_id="") -> list:
        pass

    def create_comments(
        self,
        project_id="",
        topic_id="",
        data=None,
        params=None,
    ):
        return self.post(
            f"/projects/{project_id}/topics/{topic_id}/comments",
            data=data,
        )

    def get_comment(self, project_id="", topic_id="", comment_id="") -> dict:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/comments/{comment_id}",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "comment_id": comment_id,
            },
        )

    def delete_comment(self, project_id="", topic_id="", comment_id=""):
        return self.delete(f"/projects/{project_id}/topics/{topic_id}/comments/{comment_id}")

    def update_comment(
        self,
        project_id="",
        topic_id="",
        comment_id="",
        data=None,
    ):
        return self.put(
            f"/projects/{project_id}/topics/{topic_id}/comments/{comment_id}",
            data=data,
        )

    def get_viewpoints(self, project_id="", topic_id="") -> list:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def create_viewpoints(self, project_id="", topic_id="", data=None):
        return self.post(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints",
            data=data,
        )

    def get_viewpoint(self, project_id="", topic_id="", viewpoint_id="") -> dict:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "viewpoint_id": viewpoint_id,
            },
        )

    def delete_viewpoint(
        self,
        project_id="",
        topic_id="",
        viewpoint_id="",
    ):
        return self.delete(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}",
        )

    def get_snapshot(self, project_id="", topic_id="", viewpoint_id="") -> str:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/snapshot",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "viewpoint_id": viewpoint_id,
            },
        )

    def get_bitmap(self, project_id="", topic_id="", viewpoint_id="", bitmap_id="") -> str:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/bitmaps/{bitmap_id}",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "viewpoint_id": viewpoint_id,
                "bitmap_id": bitmap_id,
            },
        )

    def get_selection(self, project_id="", topic_id="", viewpoint_id="") -> dict:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/selection",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "viewpoint_id": viewpoint_id,
            },
        )

    def get_coloring(self, project_id="", topic_id="", viewpoint_id="") -> dict:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/coloring",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "viewpoint_id": viewpoint_id,
            },
        )

    def get_visibility(self, project_id="", topic_id="", viewpoint_id="") -> dict:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/visibility",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "viewpoint_id": viewpoint_id,
            },
        )

    def get_related_topics(self, project_id="", topic_id="") -> list:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/related_topics",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def update_related_topics(
        self,
        project_id="",
        topic_id="",
        data=None,
    ):
        return self.put(
            f"/projects/{project_id}/topics/{topic_id}/related_topics",
            data=data,
        )

    def get_document_references(self, project_id="", topic_id="") -> list:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/document_references",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def create_document_reference(
        self,
        project_id="",
        topic_id="",
        data=None,
    ):
        return self.post(
            f"/projects/{project_id}/topics/{topic_id}/document_references",
            data=data,
        )

    def update_document_references(
        self,
        project_id="",
        topic_id="",
        document_reference_id="",
        data=None,
    ):
        return self.put(
            f"/projects/{project_id}/topics/{topic_id}/document_references/{document_reference_id}",
            data=data,
        )

    def get_documents(self, project_id="", topic_id="") -> list:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/documents",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def create_document(
        self,
        project_id="",
        topic_id="",
        guid=None,
        data=None,
    ):
        headers = {
            "Authorization": "Bearer " + self.get_access_token(),
            "Content-type": "application/octet-stream",
        }
        response = requests.post(
            f"/projects/{project_id}/topics/{topic_id}/documents",
            data=data,
            params={guid},
            headers=headers,
        )

    def get_document(self, project_id="", topic_id="", document_id="") -> str:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/documents/{document_id}",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "document_id": document_id,
            },
        )

    def get_topics_events(self, project_id="") -> list:
        return self.get(
            f"/projects/{project_id}/topics/events",
            {
                "project_id": project_id,
            },
        )

    def get_topic_events(self, project_id="", topic_id="") -> list:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/events",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def get_comments_events(self, project_id="") -> list:
        return self.get(
            f"/projects/{project_id}/topics/comments/events",
            {
                "project_id": project_id,
            },
        )

    def get_comment_events(self, project_id="", topic_id="", comment_id="") -> list:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/comments/{comment_id}/events",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "comment_id": comment_id,
            },
        )
