# bcf

A simple Python implementation of BCF.
Manipulation of BCF-XML is available via `bcfxml.py` and manipulation of BCF-API
is available via `bcfapi.py`.

It tries to support BCF-XML version 2.1 and 3.0, and BCF-API 3.0.

## bcfxml

The `bcfxml.load` function lets you read a BCF-XML file.
It takes care of using the right version based on the "bcf.version" file contained in the BCF package.

The BCF files are extracted and parsed on-demand, and edits are stored in memory until you call the `save` method.

```python
from bcf.bcfxml import load

# Load a project
with load("/path/to/file.bcf") as bcfxml:
    project = bcfxml.project
    print(project.name)

    # To edit a project, just modify the object directly
    bcfxml.project.name = "New name"

    # Get a dictionary of topics
    topics = bcfxml.topics

    for topic_guid, topic_handler in bcfxml.topics.items():
        topic = topic_handler.topic
        print("Topic guid is", topic.guid)
        print("Topic title is", topic.title)

        # Fetch extra data about a topic
        header = topic_handler.header
        comments = topic_handler.comments
        viewpoints = topic_handler.viewpoints

        for comment in comments:
            print(comment.guid)
            print(comment.comment)
            print(comment.author)

    # Get a particular topic
    topic = bcfxml.get_topic(guid)

    # Modify a topic
    topic.title = "New title"

    bcfxml.save()
```

## bcfapi

The `bcfapi` module lets you interact with the BCF-API standard.

```python
from bcf.v3.bcfapi import FoundationClient, BcfClient

foundation_client = FoundationClient("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET", "OPENCDE_BASEURL")
auth_methods = foundation_client.get_auth_methods()

# Our library currently only implements the authorization_code flow
if "authorization_code" in auth_methods:
    foundation_client.login()

bcf_client = BcfClient(foundation_client)

versions = foundation_client.get_versions()
for version in versions:
if "3.0" in versions:
    if version["api_id"] == "bcf" and version["version_id"] == "3.0":
        bcf_client.set_version(version)

data = bcf_client.get_projects()
print(data)
project_id = data[0]["project_id"]
print(project_id)
data = bcf_client.get_project(project_id)
print(data)
data = bcf_client.get_extensions(project_id)
print(data)
```
