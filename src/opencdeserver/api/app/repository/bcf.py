import base64
import os
import jsonpickle

from fastapi import UploadFile, HTTPException

from uuid import UUID, uuid4

from database.neo4j import MyDB, driver

from models.bcf_request import *
from models.bcf_response import *
from models.request import *


class BCFDB(MyDB):

    # implemented
    def get_projects(self, current_user: User) -> list[ProjectGET]:
        def get_projects_work(tx) -> list[ProjectGET]:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)
                WHERE u.username = $username
                AND r1.read = True
                RETURN p AS project
                """
            results = tx.run(cypher, username=current_user.username)
            project_model_list = list()
            for result in results:
                project_json = self.node_to_json(result.get("project"))
                project_model = ProjectGET(**project_json)
                project_model_list.append(project_model)
            return project_model_list

        with self.driver.session() as session:
            return session.execute_read(get_projects_work)

    # implemented
    def get_project(self, project_id: UUID, current_user: User) -> ProjectGET:
        def get_project_work(tx) -> ProjectGET:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)
                WHERE u.username = $username
                AND r1.read = True
                AND p.project_id = $project_id
                RETURN p AS project
                """
            result = tx.run(cypher, username=current_user.username, project_id=str(project_id))
            first = result.single()
            if first is None:
                raise HTTPException(status_code=404, detail="Item not found.")
            project_node = first.get("project")
            project_dict = self.node_to_json(project_node)
            return ProjectGET(**project_dict)

        with self.driver.session() as session:
            return session.execute_read(get_project_work)

    # implemented
    def put_project(self, project_id: UUID, project: ProjectPUT, current_user: User) -> ProjectGET:
        def put_project_work(tx) -> ProjectGET:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)
                WHERE u.username = $username
                AND r1.update = True
                AND p.project_id = $project_id
                SET p.name = $project_name
                RETURN p AS project
                """
            result = tx.run(
                cypher, username=current_user.username, project_id=str(project_id), project_name=project.name
            )
            first = result.single()
            if first is None:
                raise HTTPException(status_code=404, detail="Item not found.")
            project_node = first.get("project")
            project_dict = self.node_to_json(project_node)
            return ProjectGET(**project_dict)

        with self.driver.session() as session:
            return session.execute_write(put_project_work)

    # implemented
    def get_project_extensions(self, project_id: UUID, current_user: User) -> ExtensionsGET:
        def get_project_extensions_work(tx) -> ExtensionsGET:
            cypher = """
                    MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(e:Extensions)
                    WHERE u.username = $username
                    AND r1.read = True
                    AND p.project_id = $project_id
                    RETURN e AS extensions
                    """
            result = tx.run(cypher, username=current_user.username, project_id=str(project_id))
            first = result.single()
            if first is None:
                raise HTTPException(status_code=404, detail="Item not found.")
            extensions_node = first.get("extensions")
            extensions_dict = self.node_to_json(extensions_node)
            return ExtensionsGET(**extensions_dict)

        with self.driver.session() as session:
            return session.execute_read(get_project_extensions_work)

    # implemented
    # returns a collection
    def get_topics(self, project_id: str, current_user: User) -> list[TopicGET]:
        def get_topics_work(tx) -> list[TopicGET]:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)
                WHERE u.username = $username
                AND r1.read = True
                AND p.project_id = $project_id 
                RETURN t AS topic, ID(t) AS server_assigned_id
                """
            results = tx.run(cypher, username=current_user.username, project_id=str(project_id))
            topic_model_list = list()
            for result in results:
                topic_json = self.node_to_json(result.get("topic"))
                topic_json["server_assigned_id"] = result.get("server_assigned_id")
                topic_model = TopicGET(**topic_json)
                topic_model_list.append(topic_model)
            return topic_model_list

        with self.driver.session() as session:
            return session.execute_read(get_topics_work)

    # implemented
    def get_topic(self, project_id: UUID, topic_id: UUID, current_user: User) -> TopicGET:
        def get_topic_work(tx) -> TopicGET:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)
                WHERE u.username = $username
                AND r1.read = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                RETURN t AS topic, ID(t) AS server_assigned_id
                """
            result = tx.run(cypher, username=current_user.username, project_id=str(project_id), topic_id=str(topic_id))
            first = result.single()
            if first is None:
                raise HTTPException(status_code=404, detail="Item not found.")
            topic_node = first.get("topic")
            topic_dict = self.node_to_json(topic_node)
            topic_dict["server_assigned_id"] = first.get("server_assigned_id")
            return TopicGET(**topic_dict)

        with self.driver.session() as session:
            return session.execute_read(get_topic_work)

    # implemented
    def post_topic(self, project_id: UUID, topic: TopicPOST, current_user: User) -> TopicGET:
        def post_topic_work(tx) -> UUID:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)
                WHERE u.username = $username
                AND r1.createTopic = True
                AND p.project_id = $project_id
                MERGE (p)-[r2:HAS]->(t:Topic {guid: $guid})
                SET t.creation_date         = $creation_date,
                    t.modified_date         = $creation_date,
                    t.creation_author       = $username,
                    t.modified_author       = $username,
                    t.topic_type            = $topic_type,
                    t.topic_status          = $topic_status,
                    t.title                 = $title,
                    t.priority              = $priority,
                    t.index                 = $index,
                    t.assigned_to           = $assigned_to,
                    t.stage                 = $stage,
                    t.description           = $description,
                    t.due_date              = $due_date
                RETURN t AS topic, ID(t) AS server_assigned_id
                """
            if not hasattr(topic, "guid") or topic.guid is None:
                topic.guid = uuid4()
            creation_date = self.timestamp()
            print(cypher)
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                guid=str(topic.guid),
                creation_date=creation_date,
                topic_type=topic.topic_type,
                topic_status=topic.topic_status,
                title=topic.title,
                priority=topic.priority,
                index=topic.index,
                assigned_to=topic.assigned_to,
                stage=topic.stage,
                description=topic.description,
                due_date=topic.due_date,
            )
            summary = result.consume()
            if summary.counters.nodes_created < 1:
                raise HTTPException(status_code=400, detail="Item not added.")
            return topic.guid

        with self.driver.session() as session:
            topic_guid = session.execute_write(post_topic_work)
            return self.get_topic(project_id, topic_guid, current_user)

    # implemented
    def put_topic(self, project_id: UUID, topic_id: UUID, topic: TopicPUT, current_user: User) -> TopicGET:
        def put_topic_work(tx) -> bool:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)
                WHERE u.username = $username
                AND r1.update = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                SET t.topic_type        = $topic_type,
                    t.topic_status      = $topic_status,
                    t.title             = $title,
                    t.priority          = $priority,
                    t.index             = $index,
                    t.modified_date     = $modified_date,
                    t.modified_author   = $username,
                    t.assigned_to       = $assigned_to,
                    t.stage             = $stage,
                    t.description       = $description,
                    t.due_date          = $due_date
                RETURN t AS topic, ID(t) AS server_assigned_id
                """
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                topic_type=topic.topic_type,
                topic_status=topic.topic_status,
                title=topic.title,
                priority=topic.priority,
                index=topic.index,
                modified_date=self.timestamp(),
                assigned_to=topic.assigned_to,
                stage=topic.stage,
                description=topic.description,
                due_date=topic.due_date,
            )
            summary = result.consume()
            if summary.counters.properties_set < 1:
                raise HTTPException(status_code=404, detail="Item not found.")
            return True

        with self.driver.session() as session:
            session.execute_write(put_topic_work)
            return self.get_topic(project_id, topic_id, current_user)

        # implemented

    def set_topic_modified_date(self, project_id: UUID, topic_id: UUID, current_user: User) -> bool:
        def set_topic_modified_date_work(tx) -> bool:
            cypher = """
                   MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)
                   WHERE u.username = $username
                   AND r1.update = True
                   AND p.project_id = $project_id
                   AND t.guid = $topic_id
                   SET t.modified_date     = $modified_date
                """
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                modified_date=self.timestamp(),
            )
            summary = result.consume()
            if summary.counters.properties_set < 1:
                raise HTTPException(status_code=404, detail="Item not found.")
            return True

        with self.driver.session() as session:
            return session.execute_write(set_topic_modified_date_work)

    # implemented
    def delete_topic(self, project_id: UUID, topic_id: UUID, current_user: User) -> int:
        def delete_topic_work(tx) -> int:
            cypher = """
                    MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)
                    WHERE u.username = $username
                    AND r1.update = True
                    AND p.project_id = $project_id
                    AND t.guid = $topic_id
                    DETACH DELETE t
                    """
            result = tx.run(cypher, username=current_user.username, project_id=str(project_id), topic_id=str(topic_id))
            result_summary = result.consume()
            if result_summary.counters.nodes_deleted < 1:
                raise HTTPException(status_code=404, detail="Item not found.")
            return result_summary.counters.nodes_deleted

        with self.driver.session() as session:
            return session.execute_write(delete_topic_work)

    # implemented
    # returns a collection
    def get_files_information(self, project_id: UUID, current_user: User) -> list[ProjectFileInformation]:
        def get_files_information_work(tx) -> list[ProjectFileInformation]:
            cypher = """
                 MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:CONTAINS]->(d:Document)
                 WHERE u.username = $username
                 AND r1.read = True
                 AND p.project_id = $project_id
                 RETURN d AS document
                 """
            results = tx.run(cypher, username=current_user.username, project_id=str(project_id))

            project_file_informations = list()
            for result in results:
                document_json = self.node_to_json(result.get("document"))
                display_information_list = list()
                display_information_json = {"field_display_name": "File", "field_value": document_json["title"]}
                display_information_list.append(display_information_json)
                base = os.environ["KONTROLL_BASE_URL"] + "documents/1.0/document/"
                base.replace("http://", "https://")
                base.replace("https://", "open-cde-documents://")
                document_id = document_json["document_id"]
                version_index = document_json["version_index"]
                extra_path = document_id + "/version/" + str(version_index)
                reference = base + extra_path
                file_get_json = {
                    "ifc_project": document_json["ifc_project"],
                    "filename": document_json["name"],
                    "reference": reference,
                }
                project_file_information = ProjectFileInformation(
                    display_information=display_information_list, file=file_get_json
                )
                project_file_informations.append(project_file_information)
            return project_file_informations

            #
            # BCF API compatible servers offer endpoints to list project model files, which are stored on a CDE.
            # To indicate that models provided by BCF API file-references can be downloaded from the CDE using
            # the Documents API, the reference part of a file_GET response from the BCF server will include
            # the URL scheme (protocol) open-cde-documents and a link to the document_version URL on the CDE.
            #
            # The actual URL scheme (protocol) that a Client Application should
            # use to call the document_version URL should be https.
            #
            # BCF API project_file_information example:
            #
            # {
            #   "display_information": [
            #     {
            #       "field_display_name": "Model Name",
            #       "field_value": "ARCH-Z100-051"
            #     }
            #   ],
            #   "file": {
            #     "ifc_project": "0J$yPqHBD12v72y4qF6XcD",
            #     "file_name": "OfficeBuilding_Architecture_0001.ifc",
            #     "reference": "open-cde-documents://<document_version_url>"
            #   }
            # }
            #
            # In the example above, the CDE returns a value of
            # open-cde-documents://<document_version_url> for the file reference part,
            # indicating that a Documents API capable client can call https://<document_version_url>
            # to get the document version information. From there on, compatible
            # clients can retrieve metadata and the binary content of the file.
            #
            # class ProjectFileInformation(BaseModel):
            # display_information: Optional[list[ProjectFileDisplayInformation]] = None
            # file: Optional[FileGET] = None
            #
            # class ProjectFileDisplayInformation(BaseModel):
            # field_display_name: str
            # field_value: str
            #
            # class FileGET(BaseModel):
            # ifc_project: Optional[str] = None
            # ifc_spatial_structure_element: Optional[str] = None
            # filename: Optional[str] = None
            # date: Optional[str] = None
            # reference: Optional[str] = None
            #

        with self.driver.session() as session:
            return session.execute_read(get_files_information_work)

    # implemented
    # returns a collection
    def get_files(self, project_id: UUID, topic_id: UUID, current_user: User) -> list[FileGET]:
        def get_files_work(tx) -> list[FileGET]:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:REFERS_TO]->(f:Document:Model)
                WHERE u.username = $username
                AND r1.read = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                RETURN f AS file
                """
            results = tx.run(cypher, username=current_user.username, project_id=str(project_id), topic_id=str(topic_id))
            file_model_list = list()
            for result in results:
                file_json = self.node_to_json(result.get("file"))
                file_model = FileGET(**file_json)
                file_model_list.append(file_model)
            return file_model_list

        with self.driver.session() as session:
            return session.execute_read(get_files_work)

    # implemented
    def put_files(self, project_id: UUID, topic_id: UUID, files: list[FilePUT], current_user: User) -> list[FileGET]:
        def put_files_work(tx) -> bool:
            cypher_delete_references = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:REFERS_TO]->(f:Document:Model)
                WHERE u.username = $username
                AND r1.updateFiles = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                DELETE r3
            """
            tx.run(
                cypher_delete_references,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
            )
            cypher_update_and_attach_references = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(f:Document:Model)
                MATCH (u)-[r1]->(p)-[r3:HAS]->(t:Topic)
                WHERE u.username = $username
                AND r1.updateFiles = True
                AND p.project_id = $project_id
                AND f.reference = $reference
                AND t.guid = $topic_id
                SET f.filename                          = $filename,
                    f.date                              = $date,
                    f.ifc_project                       = $ifc_project,
                    f.ifc_spatial_structure_element     = $ifc_spatial_structure_element
                MERGE (t)-[r4:REFERS_TO]->(f)
                RETURN f
                """
            for file in files:
                result = tx.run(
                    cypher_update_and_attach_references,
                    username=current_user.username,
                    project_id=str(project_id),
                    reference=file.reference,
                    topic_id=str(topic_id),
                    filename=file.filename,
                    date=file.date,
                    ifc_project=file.ifc_project,
                    ifc_spatial_structure_element=file.ifc_spatial_structure_element,
                )
                first = result.single()
                if first is None:
                    raise HTTPException(status_code=404, detail="Item not found.")
                return True

        with self.driver.session() as session:
            session.execute_write(put_files_work)
            return self.get_files(project_id, topic_id, current_user)

    # implemented
    def get_comments(self, project_id: UUID, topic_id: UUID, current_user: User) -> list[CommentGET]:
        def get_comments_work(tx) -> list[CommentGET]:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(c:Comment)
                WHERE u.username = $username
                AND r1.read = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                RETURN c AS comment
                """
            results = tx.run(cypher, username=current_user.username, project_id=str(project_id), topic_id=str(topic_id))
            comment_model_list = list()
            for result in results:
                comment_json = self.node_to_json(result.get("comment"))
                comment_json["topic_guid"] = str(topic_id)
                comment_model = CommentGET(**comment_json)
                comment_model_list.append(comment_model)
            return comment_model_list

        with self.driver.session() as session:
            return session.execute_read(get_comments_work)

    # implemented
    def get_comment(self, project_id: UUID, topic_id: UUID, comment_id: UUID, current_user: User) -> CommentGET:
        def get_comment_work(tx) -> CommentGET:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(c:Comment)
                WHERE u.username = $username
                AND r1.read = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                AND c.guid = $comment_id
                RETURN c AS comment
                """
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                comment_id=str(comment_id),
            )
            first = result.single()
            if first is None:
                raise HTTPException(status_code=404, detail="Item not found.")
            comment_node = first.get("comment")
            comment_dict = self.node_to_json(comment_node)
            comment_dict["topic_guid"] = str(topic_id)
            comment = CommentGET(**comment_dict)
            return comment

        with self.driver.session() as session:
            return session.execute_read(get_comment_work)
        # date
        # author
        # topic_guid

    def post_comment(self, project_id: UUID, topic_id: UUID, comment: CommentPOST, current_user: User) -> CommentGET:
        def post_comment_work(tx) -> UUID:
            if not hasattr(comment, "guid") or comment.guid is None:
                this_comment_guid = uuid4()
            else:
                this_comment_guid = UUID(comment.guid)
            if comment.viewpoint_guid:
                # make sure that given viewpoint_guid exists in database
                viewpoints = self.get_viewpoints(project_id, topic_id, current_user)
                viewpoint_guids = [viewpoint.guid for viewpoint in viewpoints]
                if comment.viewpoint_guid not in viewpoint_guids:
                    raise HTTPException(status_code=400, detail="Item not added.")
                injection_viewpoint = "-[r3:HAS]->(v:Viewpoint)"
                injection_viewpoint_selection = "AND v.guid = $viewpoint_id"
                injection_viewpoint_relation = "MERGE (c2)-[r7:RELATED_TO]->(v)"
            else:
                injection_viewpoint = ""
                injection_viewpoint_selection = ""
                injection_viewpoint_relation = ""
            if hasattr(comment, "reply_to_comment_guid"):
                # make sure that given reply_to_comment_guid exists in database
                get_comments = self.get_comments(project_id, topic_id, current_user)
                comment_guids = [get_comment.guid for get_comment in get_comments]
                if comment.reply_to_comment_guid not in comment_guids:
                    raise HTTPException(status_code=400, detail="Item not added.")
                injection_existing_comment = "MATCH (u)-[r1]->(p)-[r2]->(t)-[r4:HAS]->(c1:Comment)"
                injection_existing_comment_selection = "AND c1.guid = $reply_to_comment_id"
                injection_existing_comment_relation = "MERGE (c1)-[r5:THEN]->(c2)"
            else:
                injection_existing_comment = ""
                injection_existing_comment_selection = ""
                injection_existing_comment_relation = ""
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)%s
                %s
                WHERE u.username = $username
                AND r1.createComment = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                %s
                %s
                MERGE (t)-[r5:HAS]->(c2:Comment {guid: $comment_id})
                %s
                %s
                SET c2.date                  = $creation_date,
                    c2.modified_date         = $creation_date,
                    c2.author                = $username,
                    c2.modified_author       = $username,
                    c2.comment               = $comment
                """ % (
                injection_viewpoint,
                injection_existing_comment,
                injection_viewpoint_selection,
                injection_existing_comment_selection,
                injection_viewpoint_relation,
                injection_existing_comment_relation,
            )
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                viewpoint_id=str(comment.viewpoint_guid),
                reply_to_comment_id="comment.reply_to_comment_guid",
                comment_id=str(this_comment_guid),
                creation_date=self.timestamp(),
                comment=comment.comment,
            )
            summary = result.consume()
            if summary.counters.nodes_created < 1:
                raise HTTPException(status_code=400, detail="Item not added.")
            return this_comment_guid

        with self.driver.session() as session:
            comment_guid = session.execute_write(post_comment_work)
            return self.get_comment(project_id, topic_id, comment_guid, current_user)

    def put_comment(
        self, project_id: UUID, topic_id: UUID, comment_id: UUID, comment: CommentPUT, current_user: User
    ) -> CommentGET:
        def put_comment_work(tx) -> bool:
            if comment.viewpoint_guid:
                viewpoints = self.get_viewpoints(project_id, topic_id, current_user)
                viewpoint_guids = [viewpoint.guid for viewpoint in viewpoints]
                if comment.viewpoint_guid not in viewpoint_guids:
                    raise HTTPException(status_code=400, detail="Item not added.")
                injection_new_viewpoint = "MATCH (t)-[r5:HAS]->(v_new:Viewpoint)"
                injection_new_viewpoint_selection = "WHERE v_new.guid = $new_rtv_id"
                injection_new_viewpoint_relation = "MERGE (c)-[r5:RELATED_TO]->(v)"
            else:
                injection_new_viewpoint = ""
                injection_new_viewpoint_selection = ""
                injection_new_viewpoint_relation = ""
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(c:Comment)
                WHERE u.username = $username
                AND r1.updateComment = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                AND c.guid = $comment_id
                OPTIONAL MATCH (c)-[r4:RELATED_TO]->(v_existing:Viewpoint)
                %s
                %s 
                SET c.comment = $comment
                SET c.modified_date = $modified_date
                SET c.modified_author = $username
                DELETE r4
                %s
            """ % (
                injection_new_viewpoint,
                injection_new_viewpoint_selection,
                injection_new_viewpoint_relation,
            )
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                comment_id=str(comment_id),
                new_rtv_id=str(comment.viewpoint_guid),
                comment=comment.comment,
                modified_date=self.timestamp(),
            )
            summary = result.consume()
            if summary.counters.properties_set < 1:
                raise HTTPException(status_code=400, detail="Item not added.")
            return True

        with self.driver.session() as session:
            session.execute_write(put_comment_work)
            return self.get_comment(project_id, topic_id, comment_id, current_user)

    # implemented
    def delete_comment(self, project_id: UUID, topic_id: UUID, comment_id: UUID, current_user: User) -> int:
        def delete_comment_work(tx) -> int:
            cypher = """
                    MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(c:Comment)
                    WHERE u.username = $username
                    AND r1.update = True
                    AND p.project_id = $project_id
                    AND t.guid = $topic_id
                    AND c.guid = $comment_id
                    DETACH DELETE c
                """
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                comment_id=str(comment_id),
            )
            result_summary = result.consume()
            if result_summary.counters.nodes_deleted < 1:
                raise HTTPException(status_code=404, detail="Item not found.")
            return result_summary.counters.nodes_deleted

        with self.driver.session() as session:
            self.set_topic_modified_date(project_id, topic_id, current_user)
            return session.execute_write(delete_comment_work)

    @staticmethod
    def enum_to_mime(enum_type) -> str:
        if str(enum_type) == "png":
            mime_type = "image/png"
        elif str(enum_type) == "jpg" or str(enum_type) == "jpeg":
            mime_type = "image/jpeg"
        else:
            mime_type = "image/" + str(enum_type)
        return mime_type

    # implementing
    def post_viewpoint(
        self, project_id: UUID, topic_id: UUID, viewpoint: ViewpointPOST, current_user: User
    ) -> ViewpointGET:
        def post_viewpoint_work(tx) -> str:
            if hasattr(viewpoint, "snapshot"):
                snapshot_type = self.enum_to_mime(viewpoint.snapshot.snapshot_type.value)
                snapshot = True
                set_snapshot = "v.snapshot = $snapshot, v.snapshot_type = $snapshot_type,"
            else:
                snapshot_type = ""
                snapshot = False
                set_snapshot = ""
            cypher_viewpoint = (
                """
                 MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)
                 WHERE u.username = $username
                 AND r1.createViewpoint = True
                 AND p.project_id = $project_id
                 AND t.guid = $topic_id
                 MERGE (t)-[r3:HAS]->(v:Viewpoint {guid: $guid, index: $index})
                 SET v.camera_definition = $camera_definition,
                     v.camera_view_point   = point({x: $cvp_x, y: $cvp_y, z: $cvp_z}),
                     v.camera_direction    = point({x: $cad_x, y: $cad_y, z: $cad_z}),
                     v.camera_up_vector    = point({x: $cuv_x, y: $cuv_y, z: $cuv_z}),
                     v.view_tws_or_fo_view = $view_tws_or_fo_view,
                     v.aspect_ratio        = $aspect_ratio,
                     %s
                     v.default_visibility = $default_visibility,
                     v.spaces_visible = $spaces_visible,
                     v.space_boundaries_visible = $space_boundaries_visible,
                     v.openings_visible = $openings_visible
                 """
                % set_snapshot
            )
            if viewpoint.guid is None:
                viewpoint.guid = uuid4()
            if viewpoint.orthogonal_camera is None:
                camera_definition = "perspective_camera"
                view_tws_or_fo_view = viewpoint.perspective_camera.field_of_view
                aspect_ratio = viewpoint.perspective_camera.aspect_ratio
                cvp = viewpoint.perspective_camera.camera_view_point
                cad = viewpoint.perspective_camera.camera_direction
                cuv = viewpoint.perspective_camera.camera_up_vector
            else:
                camera_definition = "orthogonal_camera"
                view_tws_or_fo_view = viewpoint.orthogonal_camera.view_to_world_scale
                aspect_ratio = viewpoint.orthogonal_camera.aspect_ratio
                cvp = viewpoint.orthogonal_camera.camera_view_point
                cad = viewpoint.orthogonal_camera.camera_direction
                cuv = viewpoint.orthogonal_camera.camera_up_vector
            result = tx.run(
                cypher_viewpoint,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                guid=str(viewpoint.guid),
                index=viewpoint.index,
                camera_definition=camera_definition,
                cvp_x=cvp.x,
                cvp_y=cvp.y,
                cvp_z=cvp.z,
                cad_x=cad.x,
                cad_y=cad.y,
                cad_z=cad.z,
                cuv_x=cuv.x,
                cuv_y=cuv.y,
                cuv_z=cuv.z,
                view_tws_or_fo_view=view_tws_or_fo_view,
                aspect_ratio=aspect_ratio,
                snapshot=snapshot,
                snapshot_type=snapshot_type,
                default_visibility=viewpoint.components.visibility.default_visibility,
                spaces_visible=viewpoint.components.visibility.view_setup_hints.spaces_visible,
                space_boundaries_visible=viewpoint.components.visibility.view_setup_hints.space_boundaries_visible,
                openings_visible=viewpoint.components.visibility.view_setup_hints.openings_visible,
            )
            summary = result.consume()
            if summary.counters.nodes_created < 1:
                print(cypher_viewpoint)
                raise HTTPException(status_code=400, detail="Item not added.")

            # LINES
            for line in viewpoint.lines:
                cypher_line = """
                    MATCH (v:Viewpoint)
                    WHERE v.guid = $guid
                    MERGE (v)-[r1:HAS]->(l:Line)
                    SET l.start_point = point({x: $lsp_x, y: $lsp_y, z: $lsp_z}),
                        l.end_point = point({x: $lep_x, y: $lep_y, z: $lep_z})
                """
                result = tx.run(
                    cypher_line,
                    guid=str(viewpoint.guid),
                    lsp_x=line.start_point.x,
                    lsp_y=line.start_point.y,
                    lsp_z=line.start_point.z,
                    lep_x=line.end_point.x,
                    lep_y=line.end_point.y,
                    lep_z=line.end_point.z,
                )
                summary = result.consume()
                if summary.counters.nodes_created < 1:
                    print(cypher_line)
                    raise HTTPException(status_code=400, detail="Item not added.")

            # CLIPPING PLANES
            for clipping_plane in viewpoint.clipping_planes:
                cypher_clipping_plane = """
                    MATCH (v:Viewpoint)
                    WHERE v.guid = $guid
                    MERGE (v)-[r1:HAS]->(cp:ClippingPlane)
                    SET cp.location = point({x: $cpl_x, y: $cpl_y, z: $cpl_z}),
                        cp.direction = point({x: $cpd_x, y: $cpd_y, z: $cpd_z})
                """
                result = tx.run(
                    cypher_clipping_plane,
                    guid=str(viewpoint.guid),
                    lsp_x=clipping_plane.location.x,
                    lsp_y=clipping_plane.location.y,
                    lsp_z=clipping_plane.location.z,
                    lep_x=clipping_plane.direction.x,
                    lep_y=clipping_plane.direction.y,
                    lep_z=clipping_plane.direction.z,
                )
                summary = result.consume()
                if summary.counters.nodes_created < 1:
                    print(cypher_clipping_plane)
                    raise HTTPException(status_code=400, detail="Item not added.")

            # BITMAPS
            for bitmap in viewpoint.bitmaps:
                cypher_bitmap = """
                    MATCH (v:Viewpoint)
                    WHERE v.guid = $guid
                    MERGE (v)-[r1:HAS]->(b:Bitmap)
                    SET b.type = $type,
                        b.location = point({x: $bml_x, y: $bml_y, z: $bml_z}),
                        b.normal = point({x: $bmn_x, y: $bmn_y, z: $bmn_z}),
                        b.up = point({x: $bmu_x, y: $bmu_y, z: $bmu_z}),
                        b.height = $height
                """
                bitmap_type = self.enum_to_mime(bitmap.bitmap_type)
                result = tx.run(
                    cypher_bitmap,
                    guid=str(viewpoint.guid),
                    type=bitmap_type,
                    bml_x=bitmap.location.x,
                    bml_y=bitmap.location.y,
                    bml_z=bitmap.location.z,
                    bmn_x=bitmap.direction.x,
                    bmn_y=bitmap.direction.y,
                    bmn_z=bitmap.direction.z,
                    bmu_x=bitmap.direction.x,
                    bmu_y=bitmap.direction.y,
                    bmu_z=bitmap.direction.z,
                    height=bitmap.height,
                )
                summary = result.consume()
                if summary.counters.nodes_created < 1:
                    print(bitmap_type)
                    raise HTTPException(status_code=400, detail="Item not added.")

            # COMPONENTS
            components = {}
            for selected_component in viewpoint.components.selection:
                if selected_component.ifc_guid not in components:
                    components[selected_component.ifc_guid] = {}
                components[selected_component.ifc_guid]["selected"] = True
                components[selected_component.ifc_guid]["originating_system"] = selected_component.originating_system
                components[selected_component.ifc_guid]["authoring_tool_id"] = selected_component.authoring_tool_id
            for color in viewpoint.components.coloring:
                for colored_component in color.components:
                    if colored_component.ifc_guid not in components:
                        components[colored_component.ifc_guid] = {}
                    components[colored_component.ifc_guid]["color"] = color.color
            for exception_component in viewpoint.components.visibility.exceptions:
                if exception_component.ifc_guid not in components:
                    components[exception_component.ifc_guid] = {}
                components[exception_component.ifc_guid]["visibility_exception"] = True
            set_list = list()

            for ifc_guid in components.keys():
                set_list.append("c.ifc_guid = $ifc_guid")
                if "selected" in components[ifc_guid]:
                    selected = True
                    originating_system = components[ifc_guid]["originating_system"]
                    authoring_tool_id = components[ifc_guid]["authoring_tool_id"]
                    set_list.append("c.selected = $selected")
                    set_list.append("c.originating_system = $originating_system")
                    set_list.append("c.authoring_tool_id = $authoring_tool_id")
                else:
                    selected = False
                    originating_system = False
                    authoring_tool_id = False
                if "color" in components[ifc_guid]:
                    color = components[ifc_guid]["color"]
                    set_list.append("c.color = $color")
                else:
                    color = False
                if "visibility_exception" in components[ifc_guid]:
                    visibility_exception = True
                    set_list.append("c.visibility_exception = $visibility_exception")
                else:
                    visibility_exception = False
                set_string = ", ".join(set_list)
                cypher_component = """
                    MATCH (v:Viewpoint)
                    WHERE v.guid = $viewpoint_id
                    MERGE (v)-[r1:HAS]->(c:Component {ifc_guid: $ifc_guid})
                    SET 
                """
                cypher_component += set_string
                tx.run(
                    cypher_component,
                    viewpoint_id=str(viewpoint.guid),
                    ifc_guid=str(ifc_guid),
                    selected=selected,
                    originating_system=originating_system,
                    authoring_tool_id=authoring_tool_id,
                    color=color,
                    visibility_exception=visibility_exception,
                )
                summary = result.consume()

            # Look for component UUIDs in IFC-graph and relate them
            for ifc_guid in components.keys():
                cypher_link = """
                    MATCH (prod:IfcProduct) WHERE prod.GlobalId = $uuid
                    MATCH (c:Component) WHERE c.ifc_guid = $uuid
                    MERGE (c)-[r:SAME_AS]->(prod)
                """
                tx.run(cypher_link, uuid=str(ifc_guid))
                result.consume()

                cypher_link = """
                    MATCH (prod:IfcProduct)
                        -[r1:IsDefinedBy]->(rs:IfcRelationship)
                        -[r2:RelatingPropertyDefinition]->(ps:IfcPropertySet)
                        -[r3:HasProperties]->(prop:IfcProperty)
                        -[r4:NominalValue]->(root:Root)
                        WHERE prod.GlobalId = $uuid
                        AND ps.Name = 'Reuse'
                        AND prop.Name = 'GTIN'
                    MATCH (c:Component) WHERE c.ifc_guid = $uuid
                    SET c.GTIN = root.wrappedValue
                """
                tx.run(cypher_link, uuid=str(ifc_guid))
                result.consume()

            if summary.counters.nodes_created < 1:
                print(cypher_component)
                raise HTTPException(status_code=400, detail="Item not added.")
            else:
                snapshot_path = ""
                bitmap_path = ""
                try:
                    snapshot_name = "snapshot_" + str(viewpoint.guid)
                    file_ending = "." + str(viewpoint.snapshot.snapshot_type.value)
                    snapshot_path = "data/snapshots/" + snapshot_name + file_ending
                    with open(snapshot_path, "wb") as snapshot_file:
                        snapshot_image = base64.b64decode(viewpoint.snapshot.snapshot_data, validate=True)
                        snapshot_file.write(snapshot_image)
                        snapshot_file.close()
                    for bitmap in viewpoint.bitmaps:
                        bitmap_name = "bitmap_" + str(bitmap.guid)
                        file_ending = "." + str(bitmap.bitmap_type.value)
                        bitmap_path = "data/bitmaps/" + bitmap_name + file_ending
                        with open(bitmap_path, "wb") as bitmap_file:
                            bitmap_image = base64.b64decode(bitmap.bitmap_data, validate=True)
                            bitmap_file.write(bitmap_image)
                            bitmap_file.close()
                except Exception as e:
                    print("could not create file " + snapshot_path + " " + bitmap_path + " ")
                    print(e)
                    raise HTTPException(status_code=400, detail="Item not added.")
            return viewpoint.guid

        with self.driver.session() as session:
            viewpoint.guid = session.execute_write(post_viewpoint_work)
            viewpoint.guid = UUID(viewpoint.guid)
            self.set_topic_modified_date(project_id, topic_id, current_user)
            return self.get_viewpoint(project_id, topic_id, viewpoint.guid, current_user)

    # implemented
    # returns a collection
    def get_viewpoints(self, project_id: UUID, topic_id: UUID, current_user: User) -> list[ViewpointGET]:
        def get_viewpoints_work(tx) -> list[ViewpointGET]:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(v:Viewpoint)
                WHERE u.username = $username
                AND r1.read = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                RETURN v.guid AS viewpoint_id
                """
            results = tx.run(cypher, username=current_user.username, project_id=str(project_id), topic_id=str(topic_id))
            viewpoint_model_list = list()
            for result in results:
                viewpoint_id = result.get("viewpoint_id")
                viewpoint_model = self.get_viewpoint(project_id, topic_id, viewpoint_id, current_user)
                viewpoint_model_list.append(viewpoint_model)
            return viewpoint_model_list

        with self.driver.session() as session:
            return session.execute_read(get_viewpoints_work)

    # pending
    def get_viewpoint(self, project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User) -> ViewpointGET:
        def get_viewpoint_work(tx) -> ViewpointGET:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(v:Viewpoint)
                WHERE u.username = $username
                AND r1.read = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                AND v.guid = $viewpoint_id
                RETURN v AS viewpoint
                """
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                viewpoint_id=str(viewpoint_id),
            )
            first = result.single()
            if first is None:
                raise HTTPException(status_code=404, detail="Item not found.")
            v_node = first.get("viewpoint")
            print(v_node)
            v = self.node_to_json(v_node)
            print(v)
            lines = self.get_viewpoint_lines(project_id, topic_id, viewpoint_id, current_user)
            clipping_planes = self.get_viewpoint_clipping_planes(project_id, topic_id, viewpoint_id, current_user)
            bitmaps = self.get_viewpoint_bitmaps(project_id, topic_id, viewpoint_id, current_user)
            snapshot_get = {"snapshot_type": v["snapshot_type"].split("/", 2)[1]}
            viewpoint_get = {
                "guid": v["guid"],
                "index": v["index"],
                "lines": lines,
                "clipping_planes": clipping_planes,
                "bitmaps": bitmaps,
                "snapshot": snapshot_get,
            }
            cvp = v["camera_view_point"]
            cad = v["camera_direction"]
            cuv = v["camera_up_vector"]
            camera = {
                "camera_view_point": {"x": cvp.x, "y": cvp.y, "z": cvp.z},
                "camera_direction": {"x": cad.x, "y": cad.y, "z": cad.z},
                "camera_up_vector": {"x": cuv.x, "y": cuv.y, "z": cuv.z},
                "aspect_ratio": v["aspect_ratio"],
            }
            if v["camera_definition"] == "orthogonal_camera":
                camera["view_to_world_scale"] = v["view_tws_or_fo_view"]
                viewpoint_get["orthogonal_camera"] = camera
            elif v["camera_definition"] == "perspective_camera":
                camera["field_of_view"] = v["view_tws_or_fo_view"]
                viewpoint_get["perspective_camera"] = camera
            jsonpickle.dumps(v)
            jsonpickle.dumps(viewpoint_get)
            return ViewpointGET(**viewpoint_get)

        with self.driver.session() as session:
            return session.execute_read(get_viewpoint_work)

    def get_viewpoint_lines(
        self, project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User
    ) -> list[Line]:
        def get_viewpoint_lines_work(tx) -> list[Line]:
            cypher = """
                    MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(v:Viewpoint)-[r4:HAS]->(l:Line)
                    WHERE u.username = $username
                    AND r1.read = True
                    AND p.project_id = $project_id
                    AND t.guid = $topic_id
                    AND v.guid = $viewpoint_id
                    RETURN l AS line
                    """
            results = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                viewpoint_id=str(viewpoint_id),
            )
            line_model_list = list()
            for result in results:
                line_node = result.get("line")
                line_json = {"start_point": line_node.start_point, "end_point": line_node.end_point}
                line_model = Line(**line_json)
                line_model_list.append(line_model)
            return line_model_list

        with self.driver.session() as session:
            return session.execute_read(get_viewpoint_lines_work)

    def get_viewpoint_clipping_planes(
        self, project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User
    ) -> list[ClippingPlane]:
        def get_viewpoint_clipping_planes_work(tx) -> list[ClippingPlane]:
            cypher = """
                    MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(v:Viewpoint)-[r4:HAS]->(cp:ClippingPlane)
                    WHERE u.username = $username
                    AND r1.read = True
                    AND p.project_id = $project_id
                    AND t.guid = $topic_id
                    AND v.guid = $viewpoint_id
                    RETURN cp AS clipping_plane
                    """
            results = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                viewpoint_id=str(viewpoint_id),
            )
            clipping_plane_model_list = list()
            for result in results:
                clipping_plane_json = self.node_to_json(result.get("clipping_plane"))
                clipping_plane_model = ClippingPlane(**clipping_plane_json)
                clipping_plane_model_list.append(clipping_plane_model)
            return clipping_plane_model_list

        with self.driver.session() as session:
            return session.execute_read(get_viewpoint_clipping_planes_work)

    def get_viewpoint_bitmaps(
        self, project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User
    ) -> list[BitmapGET]:
        def get_viewpoint_bitmaps_work(tx) -> list[BitmapGET]:
            cypher = """
                    MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(v:Viewpoint)-[r4:HAS]->(b:Bitmap)
                    WHERE u.username = $username
                    AND r1.read = True
                    AND p.project_id = $project_id
                    AND t.guid = $topic_id
                    AND v.guid = $viewpoint_id
                    RETURN b AS bitmap
                """
            results = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                viewpoint_id=str(viewpoint_id),
            )
            bitmap_model_list = list()
            for result in results:
                bitmap_json = self.node_to_json(result.get("bitmap"))
                bitmap_model = BitmapGET(**bitmap_json)
                bitmap_model_list.append(bitmap_model)
            return bitmap_model_list

        with self.driver.session() as session:
            return session.execute_read(get_viewpoint_bitmaps_work)

    def get_viewpoint_bitmap(
        self, project_id: UUID, topic_id: UUID, viewpoint_id: UUID, bitmap_id: UUID, current_user: User
    ) -> BitmapGET:
        def get_viewpoint_bitmap_work(tx) -> BitmapGET:
            cypher = """
                    MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(v:Viewpoint)-[r4:HAS]->(b:Bitmap)
                    WHERE u.username = $username
                    AND r1.read = True
                    AND p.project_id = $project_id
                    AND t.guid = $topic_id
                    AND v.guid = $viewpoint_id
                    AND b.guid = $bitmap_id
                    RETURN b AS bitmap
                """
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                viewpoint_id=str(viewpoint_id),
                bitmap_id=str(bitmap_id),
            )
            bitmap_json = self.node_to_json(result.get("bitmap"))
            return BitmapGET(**bitmap_json)

        with self.driver.session() as session:
            return session.execute_read(get_viewpoint_bitmap_work)

    def get_viewpoint_snapshot(self, project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User) -> str:
        def get_viewpoint_snapshot_work(tx) -> str:
            cypher = """
                 MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(v:Viewpoint)
                 WHERE u.username = $username
                 AND r1.read = True
                 AND p.project_id = $project_id
                 AND t.guid = $topic_id
                 AND v.guid = $viewpoint_id
                 AND v.snapshot IS NOT NULL
                 RETURN v.snapshot_type AS snapshot_type
                 """
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                viewpoint_id=str(viewpoint_id),
            )
            first = result.single()
            if first is None:
                raise HTTPException(status_code=404, detail="Item not found.")
            snapshot_type = first.get("snapshot_type")
            return snapshot_type

        with self.driver.session() as session:
            return session.execute_read(get_viewpoint_snapshot_work)

    def get_viewpoint_colored_components(
        self, project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User
    ) -> ColoringGET:
        def get_viewpoint_colored_components_work(tx) -> ColoringGET:
            cypher = """
                 MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(v:Viewpoint)-[r4:HAS]->(c:Component)
                 WHERE u.username = $username
                 AND r1.read = True
                 AND p.project_id = $project_id
                 AND t.guid = $topic_id
                 AND v.guid = $viewpoint_id
                 AND c.color IS NOT NULL
                 RETURN c AS component ORDER BY c.color
                 """
            results = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                viewpoint_id=str(viewpoint_id),
            )
            coloring_list = list()
            color = ""
            coloring = {}
            occasion = 0
            for result in results:
                component_json = self.node_to_json(result.get("component"))
                if component_json["color"] != color:
                    if occasion > 0:
                        coloring_list.append(coloring)
                        occasion += 1
                    color = component_json["color"]
                    coloring = {"color": color, "components": []}
                coloring["components"].append(component_json)
            coloring_list.append(coloring)
            coloring_get = {"coloring": coloring_list}
            return ColoringGET(**coloring_get)

        with self.driver.session() as session:
            return session.execute_read(get_viewpoint_colored_components_work)

    def get_viewpoint_selected_components(
        self, project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User
    ) -> SelectionGET:
        def get_viewpoint_selected_components_work(tx) -> SelectionGET:
            cypher = """
                     MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(v:Viewpoint)-[r4:HAS]->(c:Component)
                     WHERE u.username = $username
                     AND r1.read = True
                     AND p.project_id = $project_id
                     AND t.guid = $topic_id
                     AND v.guid = $viewpoint_id
                     AND c.selected IS NOT NULL
                     RETURN c AS component
                """
            results = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                viewpoint_id=str(viewpoint_id),
            )
            component_list = list()
            for result in results:
                component_json = self.node_to_json(result.get("component"))
                component_list.append(component_json)
            selection_get = {"selection": component_list}
            return SelectionGET(**selection_get)

        with self.driver.session() as session:
            return session.execute_read(get_viewpoint_selected_components_work)

    def get_viewpoint_components_visibility(
        self, project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User
    ) -> VisibilityGET:
        def get_viewpoint_components_visibility_work(tx) -> VisibilityGET:
            cypher = """
                 MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(v:Viewpoint)
                 WHERE u.username = $username
                 AND r1.read = True
                 AND p.project_id = $project_id
                 AND t.guid = $topic_id
                 AND v.guid = $viewpoint_id
                 RETURN v AS viewpoint
                 """
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                viewpoint_id=str(viewpoint_id),
            )
            first = result.single()
            if first is None:
                raise HTTPException(status_code=404, detail="Item not found.")
            viewpoint_json = self.node_to_json(first.get("viewpoint"))
            view_setup_hints = {
                "spaces_visible": viewpoint_json["spaces_visible"],
                "space_boundaries_visible": viewpoint_json["space_boundaries_visible"],
                "openings_visible": viewpoint_json["openings_visible"],
            }
            visibility = {
                "default_visibility": viewpoint_json["default_visibility"],
                "view_setup_hints": view_setup_hints,
            }
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(v:Viewpoint)-[r4:HAS]->(c:Component)
                WHERE u.username = $username
                AND r1.read = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                AND v.guid = $viewpoint_id
                AND c.visibility_exception IS NOT NULL
                RETURN c AS component
            """
            results = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                viewpoint_id=str(viewpoint_id),
            )
            component_list = list()
            for result in results:
                component_json = self.node_to_json(result.get("component"))
                component_list.append(component_json)
            visibility["exceptions"] = component_list
            visibility_get = {"visibility": visibility}
            return VisibilityGET(**visibility_get)

        with self.driver.session() as session:
            return session.execute_read(get_viewpoint_components_visibility_work)

    # implemented
    def delete_viewpoint(self, project_id: UUID, topic_id: UUID, viewpoint_id: UUID, current_user: User) -> int:
        def delete_viewpoint_work(tx) -> int:
            cypher = """
                    MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:HAS]->(v:Viewpoint)-[r4:HAS*]->(n)
                    WHERE u.username = $username
                    AND r1.update = True
                    AND p.project_id = $project_id
                    AND t.guid = $topic_id
                    AND v.guid = $viewpoint_id
                    DETACH DELETE v, n
                    """
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                viewpoint_id=str(viewpoint_id),
            )
            result_summary = result.consume()
            if result_summary.counters.nodes_deleted < 1:
                raise HTTPException(status_code=404, detail="Item not found.")
            return result_summary.counters.nodes_deleted

        with self.driver.session() as session:
            self.set_topic_modified_date(project_id, topic_id, current_user)
            return session.execute_write(delete_viewpoint_work)

    # implemented
    # returns a collection
    def get_related_topics(self, project_id: UUID, topic_id: UUID, current_user: User) -> list[TopicGET]:
        def get_related_topics_work(tx) -> list[TopicGET]:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t1:Topic)-[r3:RELATED_TO]->(t2:Topic)
                WHERE u.username = $username
                AND r1.read = True
                AND p.project_id = $project_id
                AND t1.guid = $topic_id
                RETURN t2 AS topic, ID(t2) AS server_assigned_id
                """
            results = tx.run(cypher, username=current_user.username, project_id=str(project_id), topic_id=str(topic_id))
            topic_model_list = list()
            for result in results:
                topic_json = self.node_to_json(result.get("topic"))
                topic_json["server_assigned_id"] = result.get("server_assigned_id")
                topic_model = TopicGET(**topic_json)
                topic_model_list.append(topic_model)
            return topic_model_list

        with self.driver.session() as session:
            return session.execute_read(get_related_topics_work)

    def put_related_topics(
        self, project_id: UUID, topic_id: UUID, related_topics: list[RelatedTopicPUT], current_user: User
    ) -> list[TopicGET]:
        def put_related_topics_work(tx) -> bool:
            for related_topic in related_topics:
                cypher = """
                    MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t1:Topic)
                    MATCH (p)-[r2:HAS]->(t2:Topic)
                    WHERE u.username = $username
                    AND r1.updateRelatedTopics = True
                    AND p.project_id = $project_id
                    AND t1.guid = $topic_id
                    AND t2.guid = $related_topic_id
                    MERGE (t1)-[r3:RELATED_TO]->(t2:Topic)
                """
                tx.run(
                    cypher,
                    username=current_user.username,
                    project_id=str(project_id),
                    topic_id=topic_id,
                    related_topic_id=related_topic.related_topic_guid,
                )
            return True

        with self.driver.session() as session:
            session.execute_write(put_related_topics_work)
            self.set_topic_modified_date(project_id, topic_id, current_user)
            return self.get_related_topics(project_id, topic_id, current_user)

    # returns a collection
    def get_topic_document_references(
        self, project_id: UUID, topic_id: UUID, current_user: User
    ) -> list[DocumentReferenceGET]:
        def get_topic_document_references_work(tx) -> list[DocumentReferenceGET]:
            cypher = """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)-[r3:REFERS_TO]->(d:Document)
                WHERE u.username = $username
                AND r1.read = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                RETURN
                    r3.guid AS reference_guid,
                    d.guid AS document_guid,
                    d.url AS document_url,
                    d.description AS document_description
                """
            results = tx.run(cypher, username=current_user.username, project_id=str(project_id), topic_id=str(topic_id))
            document_reference_model_list = list()
            for result in results:
                document_reference_model = DocumentReferenceGET(**result)
                document_reference_model_list.append(document_reference_model)
            return document_reference_model_list

        with self.driver.session() as session:
            return session.execute_read(get_topic_document_references_work)

    def post_topic_document_reference(
        self, project_id: UUID, topic_id: UUID, document_reference: DocumentReferencePOST, current_user: User
    ) -> list[DocumentReferenceGET]:
        def post_topic_document_reference_work(tx) -> bool:
            if document_reference.guid is None:
                document_reference.guid = uuid4()
            if document_reference.document_guid is None or len(document_reference.url) > 4 > len(
                document_reference.document_guid
            ):
                document_reference.document_guid = uuid4()
                document_url = "d.url = $url,"
            else:
                document_url = ""
                document_reference.url = ""
            cypher = (
                """
                MATCH (u:User)-[r1:HAS_ACTIONS_ON]->(p:Project)-[r2:HAS]->(t:Topic)
                WHERE u.username = $username
                AND r1.updateDocumentReferences = True
                AND p.project_id = $project_id
                AND t.guid = $topic_id
                MERGE (t)-[r3:REFERS_TO]->(d:Document {guid: $document_id})
                SET r3.guid: $document_reference_id,
                    %s
                    d.description = $description
            """
                % document_url
            )
            result = tx.run(
                cypher,
                username=current_user.username,
                project_id=str(project_id),
                topic_id=str(topic_id),
                document_id=str(document_reference.document_guid),
                document_reference_id=str(document_reference.guid),
                url=document_reference.url,
                description=document_reference.description,
            )
            summary = result.consume()
            if summary.counters.nodes_created < 1:
                raise HTTPException(status_code=400, detail="Item not added.")
            return True

        with self.driver.session() as session:
            session.execute_write(post_topic_document_reference_work)
            self.set_topic_modified_date(project_id, topic_id, current_user)
            return self.get_topic_document_references(project_id, topic_id, current_user)

    def put_topic_document_references(
        self,
        project_id: UUID,
        topic_id: UUID,
        reference_id: UUID,
        document_reference: DocumentReferencePUT,
        current_user: User,
    ) -> list[DocumentReferenceGET]:
        document_reference.guid = reference_id
        document_reference_post = DocumentReferencePOST(document_reference)
        topic_document_references_response = self.post_topic_document_reference(
            project_id, topic_id, document_reference_post, current_user
        )
        self.set_topic_modified_date(project_id, topic_id, current_user)
        return topic_document_references_response

    # returns a collection
    def get_documents(self, project_id: UUID, current_user: User):
        return True

    def post_document(self, project_id: UUID, file: UploadFile, current_user: User):
        return True

    def get_document(self, project_id: UUID, document_id: UUID, current_user: User):
        return True

    # returns a collection
    def get_topics_events(self, project_id: UUID, topic_id: UUID, current_user: User):
        return True

    # returns a collection
    def get_topic_events(self, project_id: UUID, topic_id: UUID, current_user: User):
        return True

    # returns a collection
    def get_comments_events(self, project_id: UUID, UUID, current_user: User):
        return True

    # returns a collection
    def get_comment_events(self, project_id: UUID, topic_id: UUID, comment_id: UUID, current_user: User):
        return True


bcf_db = BCFDB(driver)
