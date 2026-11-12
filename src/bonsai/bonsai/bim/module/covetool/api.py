# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import requests


class Api:
    def login(self, username, password):
        data = {
            "username": username,
            "password": password,
        }
        response_data = self.post_request("get-token", data, False)
        if "token" in response_data:
            self.token = str(response_data["token"])
            return self.token

    def post_request(self, path, data, use_token=True):
        url = self._api_url(path)
        headers = self._headers(use_token)
        response = requests.post(url, headers=headers, json=data)
        return self._handle_response(response)

    def get_request(self, path, use_token=True):
        url = self._api_url(path)
        headers = self._headers(use_token)
        response = requests.get(url, headers=headers)
        return self._handle_response(response)

    def _api_url(self, path):
        return "https://app.covetool.com/api/" + path + "/"

    def _headers(self, use_token):
        headers = {}
        if use_token:
            headers["Authorization"] = "Token " + self.token
        return headers

    def _handle_response(self, response):
        if response.ok:
            return response.json()
        else:
            return {"result": "error"}
