# bcf

A simple Python implementation of BCF. The data model is described in `data.py`.
Manipulation of BCF-XML is available via `bcfxml.py` and manipulation of BCF-API
is available via `bcfapi.py`.

 - BCF-XML version 2.1: Fully supported
 - BCF-API version 2.1: Not supported, will probably tackle this after BCF-API v3.0
 - BCF-XML version 3.0: Almost fully supported, except for the documents module
 - BCF-API version 3.0: Not supported, but work underway to support it

## bcfxml

The `bcfxml` module lets you interact with the BCF-XML standard.

```
from bcf import bcfxml


# Load a project
bcfxml = bcfxml.load("/path/to/file.bcf")


# The project is also stored in the module
# project == bcfxml.project
project=bcfxml.get_project()
print(project.name)

# To edit a project, just modify the object directly
bcfxml.project.name = "New name"
bcfxml.edit_project()

# The BCF file is extracted to this temporary directory
print(bcfxml.filepath)

# Get a dictionary of topics
topics = bcfxml.get_topics()

# Note: topics == bcfxml.topics
for guid, topic in bcfxml.topics.items():
    print("Topic guid is", guid)
    print("Topic guid is", topic.guid)
    print("Topic title is", topic.title)

    # Fetch extra data about a topic
    header = bcfxml.get_header(guid)
    comments = bcfxml.get_comments(guid)
    viewpoints = bcfxml.get_viewpoints(guid)

    # Note: comments == topic.comments, and so on
    for comment_guid, comment in comments.items():
        print(comment_guid)
        print(comment.comment)
        print(comment.author)

# Get a particular topic
topic = bcfxml.get_topic(guid)

# Modify a topic
topic.title = "New title"
bcfxml.edit_topic(topic)
```
