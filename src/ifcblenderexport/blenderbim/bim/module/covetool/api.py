import json
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
