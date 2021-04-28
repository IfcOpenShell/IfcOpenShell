import uuid
import time
import json
import urllib
import requests
import webbrowser
import http.server


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
    def __init__(self):
        self.baseurl = "https://bs-dd-api-prototype.azurewebsites.net/"
        self.access_token = ""
        self.refresh_token = ""
        self.access_token_expires_on = time.time()
        self.refresh_token_expires_on = time.time()
        self.auth_endpoint = "https://buildingsmartservices.b2clogin.com/tfp/buildingsmartservices.onmicrosoft.com/b2c_1_signupsignin/oauth2/v2.0/authorize"
        self.token_endpoint = "https://buildingsmartservices.b2clogin.com/tfp/buildingsmartservices.onmicrosoft.com/b2c_1_signupsignin/oauth2/v2.0/token"
        self.client_id = "4aba821f-d4ff-498b-a462-c2837dbbba70"

    def get(self, endpoint, params=None, is_auth_required=False):
        headers = {}
        if is_auth_required:
            headers = {"Authorization": "Bearer " + self.get_access_token()}
        return requests.get(f"{self.baseurl}{endpoint}", headers=headers, params=params or None).json()

    def post(self):
        pass  # TODO

    def get_access_token(self):
        if self.access_token and self.access_token_expires_on > time.time():
            return self.access_token
        elif self.refresh_token and self.refresh_token_expires_on > time.time():
            self.refresh_token()
        else:
            self.login()
        return self.access_token

    def login(self):
        with http.server.HTTPServer(("", 0), OAuthReceiver) as server:
            state = str(uuid.uuid4())
            query = urllib.parse.urlencode(
                {
                    "client_id": self.client_id,
                    "response_type": "code",
                    # offline_access required to get a refresh_token
                    "scope": "https://buildingsmartservices.onmicrosoft.com/api/read offline_access",
                    "state": state,
                    "redirect_uri": f"http://localhost:{server.server_address[1]}",
                }
            )
            webbrowser.open(f"{self.auth_endpoint}?{query}")
            server.timeout = 75
            server.state = state
            server.handle_request()
            if server.auth_code and server.auth_state == state:
                self.set_tokens_from_response(
                    requests.post(
                        "https://buildingsmartservices.b2clogin.com/tfp/buildingsmartservices.onmicrosoft.com/b2c_1_signupsignin/oauth2/v2.0/token",
                        params={
                            "grant_type": "authorization_code",
                            "code": server.auth_code,
                        },
                    ).json()
                )

    def refresh_token(self):
        self.set_tokens_from_response(
            requests.post(
                self.token_endpoint,
                params={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
            ).json()
        )

    def set_tokens_from_response(self, response):
        self.access_token = response["access_token"]
        self.refresh_token = response["refresh_token"]
        self.access_token_expires_on = time.time() + response["expires_in"]
        self.refresh_token_expires_on = time.time() + response["refresh_token_expires_in"]

    def Classification(self, namespaceUri, version="v3", languageCode="", includeChildClassificationReferences=True):
        return self.get(
            f"api/Classification/{version}",
            {
                "namespaceUri": namespaceUri,
                "languageCode": languageCode,
                "includeChildClassificationReferences": includeChildClassificationReferences,
            },
        )

    def Country(self, version="v1"):
        return self.get(f"api/Country/{version}")

    def Domain(self, version="v2"):
        return self.get(f"api/Domain/{version}")

    def graphql(self):
        return  # TODO

    def Language(self, version="v1"):
        return self.get(f"api/Language/{version}")

    def Property(self, namespaceUri, version="v2", languageCode=""):
        return self.get(f"api/Property/{version}", {"namespaceUri": namespaceUri, "languageCode": languageCode})

    def PropertyValue(self, namespaceUri, version="v1", languageCode=""):
        return self.get(f"api/PropertyValue/{version}", {"namespaceUri": namespaceUri, "languageCode": languageCode})

    def ReferenceDocument(self, version="v1"):
        return self.get(f"api/ReferenceDocument/{version}")

    def RequestExportFile(self):
        return  # TODO

    def SearchList(self, DomainNamespaceUri, version="v2", SearchText="", LanguageCode="", RelatedIfcEntity=""):
        return self.get(
            f"api/SearchList/{version}",
            {
                "DomainNamespaceUri": DomainNamespaceUri,
                "SearchText": SearchText,
                "LanguageCode": LanguageCode,
                "RelatedIfcEntity": RelatedIfcEntity,
            },
            is_auth_required=True,
        )

    def SearchListOpen(self, DomainNamespaceUri, version="v2", SearchText="", LanguageCode="", RelatedIfcEntity=""):
        return self.get(
            f"api/SearchListOpen/{version}",
            {
                "DomainNamespaceUri": DomainNamespaceUri,
                "SearchText": SearchText,
                "LanguageCode": LanguageCode,
                "RelatedIfcEntity": RelatedIfcEntity,
            },
        )

    def TextSearchListOpen(self):
        return  # TODO

    def Unit(self, version="v1"):
        return self.get(f"api/Unit/{version}")

    def UploadImportFile(self):
        return  # TODO


def apply_ifc_classification_properties(ifc_file, element, classificationProperties):
    import ifcopenshell
    import ifcopenshell.api
    import ifcopenshell.util.element

    psets = ifcopenshell.util.element.get_psets(element)
    for prop in classificationProperties:
        predefinedValue = prop.get("predefinedValue")
        if not predefinedValue or prop.get("propertyDomainName") != "IFC":
            continue
        pset = psets.get(prop["propertySet"])
        if pset:
            pset = ifc_file.by_id(pset["id"])
        else:
            pset = ifcopenshell.api.run("pset.add_pset", ifc_file, product=element, name=prop["propertySet"])
        if prop["dataType"] == "boolean":
            predefinedValue = predefinedValue == "TRUE"
        ifcopenshell.api.run("pset.edit_pset", pset=pset, properties={prop["name"]: predefinedValue})
