BCF
===

**BIM Collaboration Format** (BCF) is a standard by buildingSMART to manage and
exchange coordination topics between disciplines collaborating on a project.
For example, when there is an issue during the design, engineering, or
construction of a project, a topic may be created, assigned, prioritised,
commented, or linked to objects in a BIM model or camera location.

There are two implementations of BCF:

1. **BCF-XML**: an XML file-based exchange of collaboration topics. This is
   useful for mass imports, exports, data migration across CDEs, or fully
   offline implementations.
2. **BCF-API**: an online RESTful API-based management of collaboration topics.
   When topics are managed by a CDE, if the CDE follows the OpenCDE
   specification by buildingSMART, their topics may be accessed and manipulated
   using BCF.

The upstream documentation by buildingSMART for BCF is available here:

1. `BCF-XML 2.1 upstream documentation
   <https://github.com/buildingSMART/BCF-XML/tree/release_2_1/Documentation>`__.
2. `BCF-XML 3.0 upstream documentation
   <https://github.com/BuildingSMART/BCF-XML/tree/release_3_0/Documentation>`__.
3. `BCF-API 3.0 upstream documentation
   <https://github.com/buildingSMART/bcf-api>`__.

The IfcOpenShell **BCF** library supports BCF-XML version 2.1 and 3.0, and
BCF-API 3.0.

PyPI
----

.. code-block::

    pip install bcf-client

BCF-XML
-------

The ``bcfxml.load`` function lets you read a BCF-XML file.

It takes care of using the right version based on the "bcf.version" file
contained in the BCF package.

The BCF files are extracted and parsed on-demand, and edits are stored in
memory until you call the `save` method.

.. code-block:: python

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
        topic = bcfxml.get_topic(guid).topic

        # Modify a topic
        topic.title = "New title"

        bcfxml.save()

BCF-API
-------

The ``bcfapi`` module lets you interact with the BCF-API standard.

.. code-block:: python

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
