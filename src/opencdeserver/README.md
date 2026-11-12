# Kontroll BCF API server - OpenCDE APIs

## What is this?

OpenCDE APIs:
Foundation API,
BCF API,
Documents API
implemented in python,
the FastAPI framework
and the Neo4j graph database.

This is server software. To run or test this code you need to set up your server to work with a client.
This server was developed and tested using Solibri as a client. To use a client with this server you need to configure
a client id and a client key.

You also need to configure encrypted communication and authentication using HTTPS and OAuth2.
And then you need an SSL-certificate. To get an SSL-certificate you need your own domain name.
Solibri can only connect to preconfigured domains.

This means that it is not so easy to test this software.
In the future I hope an open source BCF/CDE-client can be developed to access this server.
Maybe Blender BIM in the future could be extended with such BCF/CDE-client functionality.

## Background

You can read some background information about the project here:

https://martin.wiss.se/data/bcf_ifc_graph.pdf

The name of this project is Kontroll BCF API server because it was originally
developed as a POC prototype to test if BCF API could be used for digital inspection plans
for building permits (translated as "kontroll-plan" in Swedish language).

## Code structure

/docker-compose.yml
You bring up the project using this file.

/api/Dockerfile
Contains instructions for the FastAPI container.
Referenced by /docker-compose.yml

/api/app
Contains the server application.

/api/app/main.py
This is where the application starts.
The FastAPI-container will run this script on uvicorn.
main.py will load routes from scripts in the /api/app/api folder.

/api/app/api
This is where the FastAPI routes are defined.

/api/app/repository
Routes often runs methods that will read or write data to or from a database.
This is where methods that read or write data from database are declared.

/api/app/database
Some general methods to interact with database.

/api/app/db_config
When the Neo4j container is launched it will initialize a database
with some test data from init.cypher. This initial state does not represent
all data. Model.cypher contains a more complete model.

/api/app/ifcgraph
Script to import data from IFC STEP file to Neo4j.

/api/app/models
Pydantic models used to define the JSON structures of requests and responses.
Models are arranged in files depending on if it is request or response
or both (common) or not at all (other).

/api/app/security
Contains methods for OAuth2 and a method to get the secrets used.
You need to create your own secrets and put them in the /secrets folder.
Secrets are more secure than environment values.

/api/app/templets
Jinja2 templates used to generate some webpages necessary for OAuth2 flow and Documents API flow.

/api/app/requirements.txt
Generated using pipreqs not pip freeze.

## Deployment

To get this code running properly you need:

- your own linux server, on premise or in the cloud
- a domain name and a TLS-certificate for your domain name
- a proxy server, nginx was used
- to set up your proxy server to use HTTPS
- to use proxy as bridge between docker network and remote
- proxy (outside container) and uvicorn (inside container) should access same TLS certificate
- to edit your .env file with values specific for your server and API
- to replace hard coded values in code with  specific values for your server and API
- to create three secrets and put them in the /secrets folder
- to put apoc-5.7.0-core and apoc-5.7.0-extended jars in /neo4j/plugins folder
- to put an ifcopenshell.zip in /api/app/ifcopenshell folder
- Docker and Neo4j software
- a favicon at /favicon.ico
- to run "bash restart.sh" to start and restart containers
- a BCF client, registered with client ID and secret

This code was developed and tested using Solibri Office as BCF client, however:
Solibri Office can only connect to pre-registered servers. This means that you cannot
connect to your server using a regular version of Solibri Office. If you want to use Solibri,
then you will have to first kindly ask Solibri if they want to add your server
to the list of registered servers. An alternative is to develop your own BCF client
or to use this existing BCF API client module for python to build your own client script:

https://pypi.org/project/bcf-client/

I do not know of any working BCF API client plugins for Revit or Archicad that allows
connecting to arbitrary BCF API servers. It seems like most plugins instead were developed to
only connect to a specific BCF API server. I think that is contradictory because BCF is an open standard
intended to facilitate communication between multiple clients and servers.
A BCF API client that can connect to multiple arbitrary BCF API servers would be a good thing to develop.

## TODO

The original intention of the code was just to create a prototype for private testing.
Improvements are needed to collaborate on this code or to deploy this system in production.

Suggested improvements:

- General code structure refactoring
- Better commenting
- Testing scripts, unit testing
- Better error handling
- More consistent logging
- Easier deployment
- User registration and admin system
- BCF client registration functionality
- OData to Cypher converter
- Documents API and BCF API integration
- More complete OpenAPI documentation of routes
- More complete documentation of pydantic models
- Improvements on IFC-graph
- BCF event logging
- Implement also the routes that Solibri Office does not support
- Replace hard coded values with .env values
- Improve security before any kind of deployment in production
- Making full use of native IFC (for example allowing BCF API to edit IFC directly using BIM snippets)
- Integrate BCF API BIM snippets editing with GIT commits

## Prototype

This code was developed and tested on a system using:

- Ubuntu 20
- Nginx 1.18
- Lets encrypt, certbot
- Docker 20

## Suggested reading

### API

- FastAPI documentation
  https://fastapi.tiangolo.com/

- Building Python Microservices with FastAPI
  https://www.packtpub.com/product/building-python-microservices-with-fastapi/9781803245966

- Building Python Web APIs with FastAPI
  https://www.packtpub.com/product/building-python-web-apis-with-fastapi/9781801076630

- Building Data Science Applications with FastAPI - Second Edition
  https://www.packtpub.com/product/building-data-science-applications-with-fastapi-second-edition/9781837632749

- Pydantic docs
https://docs.pydantic.dev/latest/

- OData v4
https://www.odata.org/documentation/

### OAuth2

- Mastering OAuth 2.0
https://www.packtpub.com/product/mastering-oauth-20/9781784395407

- OAuth 2.0 Cookbook
https://www.packtpub.com/product/oauth-20-cookbook/9781788295963

- OAuth2 with Password (and hashing), Bearer with JWT tokens
https://fastapi.tiangolo.com/ur/tutorial/security/oauth2-jwt/

- Authorization Code Flow
https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow

- What is the OAuth 2.0 Authorization Code Grant Type?
https://developer.okta.com/blog/2018/04/10/oauth-authorization-code-grant-type

### Neo4j and Cypher

- Neo4j Cypher Manual
https://neo4j.com/docs/cypher-manual/current/introduction/

- Using Neo4j from python
https://neo4j.com/docs/getting-started/languages-guides/neo4j-python/

- Building Neo4j Applications with Python
https://graphacademy.neo4j.com/courses/app-python/

- The Property Graph Model
https://neo4j.com/developer/graph-database/#property-graph

### OpenCDE APIs

- BCF API
https://github.com/buildingSMART/BCF-API

- Documents API
https://github.com/buildingSMART/documents-API

- Foundation API
https://github.com/buildingSMART/foundation-API

- Open CDE APIs OAuth2 Example
https://github.com/buildingSMART/foundation-API/blob/v1.0/OAuth2Examples.md

### Server

- Docker documentation
https://docs.docker.com/

- Docker Compose overview
https://docs.docker.com/compose/

- How to use secrets in Docker Compose
https://docs.docker.com/compose/use-secrets/

- NGINX Reverse Proxy documentation
https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/

- Certbot documentation
https://eff-certbot.readthedocs.io/en/stable/

### IFC

- Native IFC
https://github.com/brunopostle/ifcmerge/blob/main/docs/whitepaper.rst

- IFC Specifications Database
https://technical.buildingsmart.org/standards/ifc/ifc-schema-specifications/

- IFC-graph for facilitating building information access and query
https://www.sciencedirect.com/science/article/pii/S0926580523000389

- IFCOpenShell documentation
https://docs.ifcopenshell.org/

### Frontend

- Jinja2 Documentation
https://svn.python.org/projects/external/Jinja-2.1.1/docs/_build/html/index.html

- Bootstrap
https://getbootstrap.com/docs/4.1/getting-started/introduction/

- jQuery
https://api.jquery.com/

## License

The GNU Affero General Public License is a free,
copyleft license for software and other kinds of works,
specifically designed to ensure cooperation with the community
in the case of network server software.

https://www.gnu.org/licenses/agpl-3.0.en.html

See the /LICENSE file.