# BCF - BCF Python library
# Copyright (C) 2021 Prabhat Singh <singh01prabhat@gmail.com>
#
# This file is part of BCF.
#
# BCF is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BCF is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BCF.  If not, see <http://www.gnu.org/licenses/>.

import base64
import http.server
import os
import tempfile
import time
import urllib
import uuid
import webbrowser
from re import A
from typing import Any, Optional, Tuple

import requests

client_id, client_secret = "", ""


class OAuthReceiver(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        self.server.auth_code = query.get("code", [""])[0]  # type:ignore
        self.server.auth_state = query.get("state", [""])[0]  # type:ignore
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("You have now authenticated :) You may now close this browser window.".encode("utf-8"))


class FoundationClient:
    def __init__(
        self, client_id: str, client_secret: str, base_url: Optional[str] = None, redirect_subdir: Optional[str] = None
    ) -> None:
        self.baseurl = base_url
        self.access_token = ""
        self.refresh_token = ""
        self.access_token_expires_on = time.time()
        self.refresh_token_expires_on = float("inf")
        self.token_endpoint = ""
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_method: Optional[str] = None
        self.redirect_subdir = redirect_subdir

    def get_access_token(self) -> str:
        if self.access_token and self.access_token_expires_on > time.time():
            return self.access_token
        elif self.refresh_token and self.refresh_token_expires_on > time.time():
            self.get_refresh_token()
        else:
            self.login()
        return self.access_token

    def get_auth_methods(self) -> list[Any]:
        resp = requests.get(f"{self.baseurl}foundation/1.0/auth")
        return resp.json()["supported_oauth2_flows"]

    def get_versions(self) -> list[Any]:
        resp = requests.get(f"{self.baseurl}foundation/versions")
        return resp.json()["versions"]

    def login(self) -> None:
        resp = requests.get(f"{self.baseurl}foundation/1.0/auth")
        values = resp.json()
        auth_endpoint = values["oauth2_auth_url"]
        self.token_endpoint = values["oauth2_token_url"]

        with http.server.HTTPServer(("", 8080), OAuthReceiver) as server:
            state = str(uuid.uuid4())
            query = urllib.parse.urlencode(
                {
                    "client_id": self.client_id,
                    "response_type": "code",
                    "state": state,
                    "redirect_uri": f"http://localhost:{server.server_address[1]}/{self.redirect_subdir}",
                }
            )
            if "?" in auth_endpoint:
                webbrowser.open(f"{auth_endpoint}&{query}")
            else:
                webbrowser.open(f"{auth_endpoint}?{query}")
            server.timeout = 100
            server.handle_request()
            if server.auth_code and server.auth_state == state:  # pylint: disable=E1101
                data = {
                    "grant_type": "authorization_code",
                    "code": server.auth_code,  # pylint: disable=E1101 type:ignore
                    "redirect_uri": f"http://localhost:{server.server_address[1]}/{self.redirect_subdir}",
                }
                headers = self._get_access_token_headers()
                self.set_tokens_from_response(requests.post(self.token_endpoint, data=data, headers=headers))

    def get_refresh_token(self) -> None:
        self.set_tokens_from_response(
            requests.post(
                self.token_endpoint,
                params={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
            ).json()
        )

    def get_new_access_token(self) -> None:
        headers = self._get_access_token_headers()
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

    def _get_access_token_headers(self) -> dict[str, str]:
        auth_string = f"{self.client_id}:{self.client_secret}"
        header_string = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
        return {"Authorization": f"Basic {header_string}"}

    def set_auth_method(self, method: str = "authorization_code_grant") -> None:
        if method != "authorization_code_grant":
            raise NotImplementedError(f"{method} not supported")
        else:
            self.auth_method = method

    def set_tokens_from_response(self, response: requests.Response) -> None:
        response_dict = response.json()
        self.access_token = response_dict["access_token"]
        self.refresh_token = response_dict["refresh_token"]
        self.access_token_expires_on = time.time() + response_dict["expires_in"]
        if "refresh_token_expires_in" in response_dict:
            self.refresh_token_expires_on = time.time() + response_dict["refresh_token_expires_in"]


class BcfClient:
    def __init__(self, foundation_client: FoundationClient) -> None:
        self.foundation_client = foundation_client
        self.version_id: Optional[str] = None
        self.baseurl: Optional[str] = None
        self.filepath = tempfile.mkdtemp()

    def set_version(self, version: dict[str, str]) -> None:
        self.version_id = version["version_id"]
        self.baseurl = version["api_base_url"]

    def get(self, endpoint: str, params: Any = None, is_auth_required: bool = False) -> Any:
        # TODO: handle error http status codes and raise exception. Follow error.json standard.
        headers = {"Authorization": f"Bearer {self.foundation_client.get_access_token()}"}

        response = requests.get(f"{self.baseurl}{endpoint}", headers=headers, params=params or None)
        try:
            response = requests.get(f"{self.baseurl}{endpoint}", headers=headers, params=params or None)
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"message: {response.reason}'   '{response.status_code}'   '{ e }")

    def post(self, endpoint: str, data: Any = None, params: Any = None) -> Tuple[int, str]:
        headers = {
            "Authorization": f"Bearer {self.foundation_client.get_access_token()}",
            "Content-type": "application/json",
        }

        try:
            response = requests.post(
                f"{self.baseurl}{endpoint}", headers=headers, params=params or None, data=data or None
            )

            if response.status_code != 201:
                response.raise_for_status()
            return response.status_code, response.text
        except requests.exceptions.HTTPError as errh:
            print(f"message: {response.reason}'  '{response.status_code}, {errh}")
            return response.status_code, response.reason

    def put(self, endpoint: str, data: Any = None, params: Any = None) -> Tuple[int, str]:
        headers = {
            "Authorization": f"Bearer {self.foundation_client.get_access_token()}",
            "Content-type": "application/json",
        }

        try:
            response = requests.put(
                f"{self.baseurl}{endpoint}", headers=headers, params=params or None, data=data or None
            )

            if response.status_code != 200:
                response.raise_for_status()
            return response.status_code, response.text
        except requests.exceptions.HTTPError as errh:
            print(f"message: {response.reason}'  '{response.status_code}, {errh}")
            return response.status_code, response.reason

    def delete(self, endpoint: str, params: Any = None) -> Tuple[int, str]:
        headers = {
            "Authorization": f"Bearer {self.foundation_client.get_access_token()}",
            "Content-type": "application/json",
        }

        try:
            response = requests.delete(f"{self.baseurl}{endpoint}", headers=headers, params=params or None)

            if response.status_code != 200:
                response.raise_for_status()
            return response.status_code, response.text
        except requests.exceptions.HTTPError as errh:
            print(f"message: {response.reason}'  '{response.status_code}, {errh}")
            return response.status_code, response.reason

    def get_projects(self) -> list[Any]:
        return self.get("/projects")

    def get_project(self, project_id: str = "") -> dict[str, Any]:
        return self.get(
            f"/projects/{project_id}",
            {
                "project_id": project_id,
            },
        )

    def update_project(self, project_id: str = "", data: Any = None) -> Tuple[int, str]:
        url = f"{self.baseurl}/projects/{project_id}"
        headers = {"Authorization": f"Bearer {self.foundation_client.get_access_token()}"}
        resp = requests.put(url, headers=headers, data=data)
        return resp.status_code, resp.text

    def get_extensions(self, project_id: str = "") -> dict[str, Any]:
        return self.get(
            f"/projects/{project_id}/extensions",
            {
                "project_id": project_id,
            },
        )

    def get_topics(
        self,
        project_id: str = "",
        topics: str = "",
        query_string: Optional[str] = None,
    ) -> list[Any]:
        # return self.get(
        #     f"/projects/{project_id}/topics",
        #     {
        #         "project_id": project_id,
        #         "topics": topics,
        #         "query_string": query_string,
        #     },
        # )
        pass

    def get_topic(self, project_id: str = "", topic_id: str = "") -> dict[str, Any]:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def create_topic(self, project_id: str = "", data: Any = None) -> Tuple[int, str]:
        return self.post(f"/projects/{project_id}/topics", data=data)

    def update_topic(self, project_id: str = "", topic_id: str = "", data: Any = None) -> Tuple[int, str]:
        return self.put(f"/projects/{project_id}/topics/{topic_id}", data=data)

    def delete_topic(self, project_id: str = "", topic_id: str = "") -> Tuple[int, str]:
        return self.delete(f"/projects/{project_id}/topics/{topic_id}")

    def get_snippet(self, project_id: str = "", topic_id: str = "") -> Tuple[int, str]:
        headers = {
            "Authorization": f"Bearer {self.foundation_client.get_access_token()}",
            "Content-type": "application/octet-stream",
        }

        response = requests.get(f"{self.baseurl}/projects/{project_id}/topics/{topic_id}/snippet", headers=headers)
        content = response.content.decode("utf-8")
        with open(os.path.join(self.filepath, f"{project_id}_{topic_id}_snippet.txt"), "w") as f:
            f.write(content)
        return response.status_code, content

    def update_snippet(self, project_id: str = "", topic_id: str = "", files: Any = None, data: Any = None) -> int:
        headers = {
            "Authorization": f"Bearer {self.foundation_client.get_access_token()}",
            "Content-type": "application/octet-stream",
        }

        response = requests.put(
            f"{self.baseurl}/projects/{project_id}/topics/{topic_id}/snippet", headers=headers, files=files
        )

        return response.status_code

    def get_files_information(self, project_id: str = "") -> list[Any]:
        return self.get(
            f"/projects/{project_id}/files_information",
            {
                "project_id": project_id,
            },
        )

    def get_files(self, project_id: str = "", topic_id: str = "") -> list[Any]:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/files",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def update_files(
        self,
        project_id: str = "",
        topic_id: str = "",
        data: Any = None,
        params: Any = None,
    ) -> Tuple[int, str]:
        return self.put(
            f"/projects/{project_id}/topics/{topic_id}/files",
            data=data,
        )

    def get_comments(self, project_id: str = "", topic_id: str = "") -> None:
        pass

    def create_comments(
        self,
        project_id: str = "",
        topic_id: str = "",
        data: Any = None,
        params: Any = None,
    ) -> Tuple[int, str]:
        return self.post(
            f"/projects/{project_id}/topics/{topic_id}/comments",
            data=data,
        )

    def get_comment(self, project_id: str = "", topic_id: str = "", comment_id: str = "") -> dict[str, Any]:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/comments/{comment_id}",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "comment_id": comment_id,
            },
        )

    def delete_comment(self, project_id: str = "", topic_id: str = "", comment_id: str = "") -> Tuple[int, str]:
        return self.delete(f"/projects/{project_id}/topics/{topic_id}/comments/{comment_id}")

    def update_comment(
        self,
        project_id: str = "",
        topic_id: str = "",
        comment_id: str = "",
        data: Any = None,
    ) -> Tuple[int, str]:
        return self.put(
            f"/projects/{project_id}/topics/{topic_id}/comments/{comment_id}",
            data=data,
        )

    def get_viewpoints(self, project_id: str = "", topic_id: str = "") -> list[Any]:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def create_viewpoints(self, project_id: str = "", topic_id: str = "", data: Any = None) -> Tuple[int, str]:
        return self.post(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints",
            data=data,
        )

    def get_viewpoint(self, project_id: str = "", topic_id: str = "", viewpoint_id: str = "") -> dict[str, Any]:
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
        project_id: str = "",
        topic_id: str = "",
        viewpoint_id: str = "",
    ) -> Tuple[int, str]:
        return self.delete(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}",
        )

    def get_snapshot(self, project_id: str = "", topic_id: str = "", viewpoint_id: str = "") -> str:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/snapshot",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "viewpoint_id": viewpoint_id,
            },
        )

    def get_bitmap(self, project_id: str = "", topic_id: str = "", viewpoint_id: str = "", bitmap_id: str = "") -> str:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/bitmaps/{bitmap_id}",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "viewpoint_id": viewpoint_id,
                "bitmap_id": bitmap_id,
            },
        )

    def get_selection(self, project_id: str = "", topic_id: str = "", viewpoint_id: str = "") -> dict[str, Any]:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/selection",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "viewpoint_id": viewpoint_id,
            },
        )

    def get_coloring(self, project_id: str = "", topic_id: str = "", viewpoint_id: str = "") -> dict[str, Any]:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/coloring",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "viewpoint_id": viewpoint_id,
            },
        )

    def get_visibility(self, project_id: str = "", topic_id: str = "", viewpoint_id: str = "") -> dict[str, Any]:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/visibility",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "viewpoint_id": viewpoint_id,
            },
        )

    def get_related_topics(self, project_id: str = "", topic_id: str = "") -> list[Any]:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/related_topics",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def update_related_topics(
        self,
        project_id: str = "",
        topic_id: str = "",
        data: Any = None,
    ) -> Tuple[int, str]:
        return self.put(
            f"/projects/{project_id}/topics/{topic_id}/related_topics",
            data=data,
        )

    def get_document_references(self, project_id: str = "", topic_id: str = "") -> list[Any]:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/document_references",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def create_document_reference(
        self,
        project_id: str = "",
        topic_id: str = "",
        data: Any = None,
    ) -> Tuple[int, str]:
        return self.post(
            f"/projects/{project_id}/topics/{topic_id}/document_references",
            data=data,
        )

    def update_document_references(
        self,
        project_id: str = "",
        topic_id: str = "",
        document_reference_id: str = "",
        data: Any = None,
    ) -> Tuple[int, str]:
        return self.put(
            f"/projects/{project_id}/topics/{topic_id}/document_references/{document_reference_id}",
            data=data,
        )

    def get_documents(self, project_id: str = "", topic_id: str = "") -> list[Any]:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/documents",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def create_document(
        self, project_id: str = "", topic_id: str = "", guid: Optional[str] = None, files: Any = None, data: Any = None
    ) -> int:
        headers = {
            "Authorization": f"Bearer {self.foundation_client.get_access_token()}",
            "Content-type": "application/octet-stream",
        }

        response = requests.post(
            f"/projects/{project_id}/topics/{topic_id}/documents",
            data=data,
            params={"guid": guid},
            files=files,
            headers=headers,
        )

        return response.status_code

    def get_document(self, project_id: str = "", topic_id: str = "", document_id: str = "") -> Tuple[int, str]:
        headers = {
            "Authorization": f"Bearer {self.foundation_client.get_access_token()}",
            "Content-type": "application/octet-stream",
        }

        response = requests.get(f"{self.baseurl}/projects/{project_id}/topics/documents/{document_id}", headers=headers)
        content = response.content.decode("utf-8")
        with open(os.path.join(self.filepath, f"{project_id}_{topic_id}_{document_id}_document.txt"), "w") as f:
            f.write(content)
        return response.status_code, content

    def get_topics_events(self, project_id: str = "") -> list[Any]:
        return self.get(
            f"/projects/{project_id}/topics/events",
            {
                "project_id": project_id,
            },
        )

    def get_topic_events(self, project_id: str = "", topic_id: str = "") -> list[Any]:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/events",
            {
                "project_id": project_id,
                "topic_id": topic_id,
            },
        )

    def get_comments_events(self, project_id: str = "") -> list[Any]:
        return self.get(
            f"/projects/{project_id}/topics/comments/events",
            {
                "project_id": project_id,
            },
        )

    def get_comment_events(self, project_id: str = "", topic_id: str = "", comment_id: str = "") -> list[Any]:
        return self.get(
            f"/projects/{project_id}/topics/{topic_id}/comments/{comment_id}/events",
            {
                "project_id": project_id,
                "topic_id": topic_id,
                "comment_id": comment_id,
            },
        )
