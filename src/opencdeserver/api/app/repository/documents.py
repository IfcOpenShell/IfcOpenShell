import os
import math

from uuid import UUID, uuid4
from typing import Union

from fastapi import HTTPException

from database.neo4j import MyDB, driver

from models.documents_request import *
from models.documents_response import *
from models.documents_common import *
from models.documents_other import *

import ifcopenshell
from py2neo import Graph

from ifcgraph.ifcgraph import create_full_graph


class DOCDB(MyDB):

    # ---- GENERAL FUNCTIONS ----

    def document_node_to_model(self, document_node):
        document_json = self.node_to_json(document_node)
        document_json["creation_date"] = self.bcf_time(document_json["creation_date"])
        document_json["file_description"] = {
            "name": document_json.pop("name", "<no name>"),
            "size_in_bytes": document_json.pop("size_in_bytes", 0),
        }
        document_json["links"] = self.document_version_links(document_json)
        return DocumentVersion(**document_json)

    def get_document(self, document_id, version_index=False):
        def get_document_work(tx) -> Union[Document, bool]:

            if version_index is None or version_index is False or not isinstance(version_index, int):
                version_index_criteria = ""
            else:
                version_index_criteria = "AND d.version_index = $version_index"

            cypher = (
                """
                MATCH (d:Document)
                WHERE d.document_id = $document_id
                %s
                RETURN d AS document
                ORDER by d.version_index DESC
                LIMIT 1
            """
                % version_index_criteria
            )

            result = tx.run(cypher, document_id=document_id, version_index=version_index)

            first = result.single()
            if first is None:
                print("There were no such document version.")
                return False

            document_node = first.get("document")
            return self.document_node_to_model(document_node)

        with self.driver.session() as session:
            return session.execute_read(get_document_work)

    # ---- CUSTOM (NON DOCUMENTS API) UPLOAD FUNCTION ----

    def create_node_for_uploaded_file(self, selection_session, project, document_version) -> Union[Document, bool]:
        def create_document_node_work(tx) -> bool:
            cypher = """
                MATCH (ss:Session:Select)<-[r1:HAS]-(u:User)-[r2:HAS_ACTIONS_ON]->(p:Project)
                WHERE ss.selection_session = $selection_session
                AND p.project_id = $project
                CREATE (p)-[r3:CONTAINS]->(d:Document)
                SET
                    d.document_id = $document_id,
                    d.session_file_id = $session_file_id,
                    d.version_index = $version_index,
                    d.version_number = $version_number,
                    d.creation_date = $creation_date,
                    d.title = $title,
                    d.original_file_name = $original_file_name,
                    d.file_ending = $file_ending,
                    d.mime_type = $mime_type,
                    d.file_type = $file_type,
                    d.name = $name,
                    d.size_in_bytes = $size_in_bytes
            """
            result = tx.run(
                cypher,
                selection_session=selection_session,
                project=project,
                document_id=document_version.document_id,
                session_file_id=document_version.session_file_id,
                version_index=document_version.version_index,
                version_number=document_version.version_number,
                creation_date=document_version.creation_date,
                title=document_version.title,
                original_file_name=document_version.original_file_name,
                file_ending=document_version.file_ending,
                mime_type=document_version.mime_type,
                file_type=document_version.file_type,
                name=document_version.file_description.name,
                size_in_bytes=document_version.file_description.size_in_bytes,
            )

            summary = result.consume()
            if summary.counters.nodes_created < 1:
                raise HTTPException(status_code=400, detail="Document node was not created.")
            return True

        def find_document_node_work(tx) -> Union[Document, bool]:
            cypher = """
                MATCH (d:Document)
                WHERE d.document_id = $document_id
                RETURN d AS document
                ORDER by d.version_index DESC
                LIMIT 1
            """

            result = tx.run(cypher, document_id=document_version.document_id)

            first = result.single()
            if first is None:
                print("There were no such document version.")
                return False

            document_node = first.get("document")
            return self.document_node_to_model(document_node)

        with self.driver.session() as session:
            if session.execute_write(create_document_node_work):
                return self.get_document(document_version.document_id, document_version.version_index)

    def create_ifc_graph_for_document(self, document_id):
        document = self.get_document(document_id)
        my_ifc_file = ifcopenshell.open("./data/documents/" + document.file_description.name)
        my_graph = Graph(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_INITIAL_PASSWORD"]))
        create_full_graph(my_graph, my_ifc_file)

    # ---- UPLOAD FUNCTIONS ----

    def post_upload_documents(
        self, upload_documents: UploadDocuments, current_user: User
    ) -> DocumentUploadSessionInitialization:
        def post_upload_documents_work(tx) -> DocumentUploadSessionInitialization:

            session_uuid = str(uuid4())
            session_callback_timedelta = int(upload_documents.callback.expires_in)
            session_url_validity_timedelta = 10 + int(os.environ["SESSION_URL_VALIDITY_SECONDS"])
            if not hasattr(upload_documents, "server_context") or not upload_documents.server_context:
                upload_documents.server_context = False

            cypher = """
                MATCH (u:User)
                WHERE u.username = $username
                CREATE (u)-[r1:HAS]->(s:Session:Upload)-[r2:HAS]->(l:Link)
                WITH *
                CALL apoc.ttl.expireIn(s, $session_callback_timedelta, 's')
                CALL apoc.ttl.expireIn(l, $session_url_timedelta, 's')
                SET
                    s.server_context = $server_context,
                    s.upload_session = $upload_session,
                    s.callback = $callback,
                    s.session_url_timedelta = $session_url_timedelta,
                    s.session_callback_timedelta = $session_callback_timedelta
            """

            result = tx.run(
                cypher,
                username=current_user.username,
                session_callback_timedelta=session_callback_timedelta,
                session_url_timedelta=session_url_validity_timedelta,
                server_context=upload_documents.server_context,
                upload_session=session_uuid,
                callback=upload_documents.callback.url,
            )

            summary = result.consume()
            if summary.counters.nodes_created < 2:
                raise HTTPException(status_code=400, detail="Session or link node was not created.")

            for file in upload_documents.files:

                cypher = """
                    MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:HAS]->(l:Link)
                    WHERE u.username = $username
                    AND us.upload_session = $upload_session
                    CREATE (us)-[r3:CONTAINS]->(d:Document:Temporary)
                    WITH *
                    CALL apoc.ttl.expireIn(d, $session_callback_timedelta, 's')
                    SET
                        d.original_file_name = $original_file_name,
                        d.name = $name,
                        d.session_file_id = $session_file_id,
                        d.document_id = $document_id,
                        d.creation_date = $creation_date,
                        d.file_ending = $file_ending,
                        d.mime_type = $mime_type,
                        d.file_type = $file_type
                """

                if not hasattr(file, "document_id") or not file.document_id:
                    # When document_id is present, this indicates that
                    # this upload is a new version of an existing document.
                    # When not present, we create a new uuid as new document_id.
                    file.document_id = doc_db.new_uuid()

                if file.file_name.lower().endswith(tuple(file_types)):
                    file_ending = file.file_name.split(".")[-1].lower()
                    name = file.document_id + "." + file_ending
                else:
                    file_ending = ""
                    name = file.document_id

                print("File ending: ", file_ending)

                mime_type = ""
                file_type = ""

                if hasattr(file_types, file_ending):

                    print("We have this file ending in dict: ", file_ending)

                    mime_type = file_types[file_ending]["mime_type"]
                    file_type = file_types[file_ending]["file_type"]

                result = tx.run(
                    cypher,
                    username=current_user.username,
                    upload_session=session_uuid,
                    session_callback_timedelta=session_callback_timedelta,
                    original_file_name=file.file_name,
                    name=name,
                    session_file_id=file.session_file_id,
                    document_id=file.document_id,
                    creation_date=doc_db.timestamp(),
                    file_ending=file_ending,
                    mime_type=mime_type,
                    file_type=file_type,
                )

                summary = result.consume()
                if summary.counters.nodes_created < 1:
                    raise HTTPException(status_code=400, detail="Document node was not created.")

            session_init = DocumentUploadSessionInitialization(
                upload_ui_url=os.environ["KONTROLL_BASE_URL"]
                + "documents/1.0/"
                + "document-upload?upload_session="
                + session_uuid,
                expires_in=os.environ["SESSION_URL_VALIDITY_SECONDS"],
                max_size_in_bytes=os.environ["SESSION_MAX_FILE_SIZE_BYTES"],
            )

            return session_init

        with self.driver.session() as session:
            return session.execute_write(post_upload_documents_work)

    # implemented
    def get_data_for_upload_documents(self, upload_session: UUID) -> UploadDocuments:
        def get_data_for_upload_documents_work(tx) -> UploadDocuments:
            # to get the documents
            cypher = """             
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:HAS]->(l:Link),
                (us)-[r3:CONTAINS]->(d:Document:Temporary)
                WHERE us.upload_session = $upload_session
                RETURN d AS document
                """
            results = tx.run(cypher, upload_session=str(upload_session))
            document_list = list()
            for result in results:
                document_json = self.node_to_json(result.get("document"))
                file_to_upload = {
                    "file_name": document_json["original_file_name"],
                    "session_file_id": document_json["session_file_id"],
                    "document_id": document_json["document_id"],
                }
                document_model = FileToUpload(**file_to_upload)
                document_list.append(document_model)

            # to get the documents
            cypher = """             
                MATCH (p:Project)<-[r1:HAS_ACTIONS_ON]-(u:User)-[r2:HAS]->(us:Session:Upload)
                WHERE us.upload_session = $upload_session
                RETURN p AS project
            """
            results = tx.run(cypher, upload_session=str(upload_session))
            project_list = list()
            for result in results:
                project_json = self.node_to_json(result.get("project"))
                project = {
                    "project_id": project_json["project_id"],
                    "name": project_json["name"],
                }
                print("Project: ", project)
                project_list.append(project)

            # to get the user and some session data
            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:HAS]->(l:Link)
                WHERE us.upload_session = $upload_session
                RETURN
                    us.server_context AS server_context,
                    us.callback AS callback,
                    us.session_callback_timedelta AS session_callback_timedelta,
                    u AS user
                """
            result = tx.run(cypher, upload_session=str(upload_session))

            first = result.single()
            if first is None:
                raise HTTPException(status_code=401, detail="No session or link.")

            user_node = first.get("user")
            user_dict = self.node_to_json(user_node)

            for_upload_documents_dict = dict()
            for_upload_documents_dict["server_context"] = first.get("server_context")

            callback_link = dict()
            callback_link["url"] = first.get("callback")
            callback_link["expires_in"] = first.get("session_callback_timedelta")

            for_upload_documents_dict["callback"] = callback_link
            for_upload_documents_dict["documents"] = document_list
            print("Project list: ", project_list)

            for_upload_documents_dict["projects"] = project_list
            for_upload_documents_dict["current_user"] = user_dict

            print("Documents list:", document_list)

            for_upload_documents_model = DataForUploadDocuments(**for_upload_documents_dict)

            return for_upload_documents_model

        with self.driver.session() as session:
            return session.execute_read(get_data_for_upload_documents_work)

    def save_metadata_for_documents(self, document, upload_session, username):
        def save_metadata_for_documents_work(tx) -> DocumentVersion:
            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:CONTAINS]->(d:Document)
                    WHERE u.username = $username
                    AND us.upload_session = $upload_session
                    AND d.session_file_id = $session_file_id
                SET
                    d.version_number = $version_number,
                    d.version_index = $version_index,
                    d.title = $title,
                    d.project = $project
            """
            result = tx.run(
                cypher,
                username=username,
                upload_session=upload_session,
                session_file_id=document.session_file_id,
                version_number=document.version_number,
                version_index=False,
                title=document.title,
                project=document.project,
            )

            summary = result.consume()
            if summary.counters.properties_set < 4:
                raise HTTPException(status_code=400, detail="All properties were not set.")

            return document.session_file_id

        with self.driver.session() as session:
            return session.execute_write(save_metadata_for_documents_work)

    def get_upload_instructions(self, upload_session, server_context, document: UploadFileDetail, user: User):
        def update_file_size_work(tx) -> str:
            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:CONTAINS]->(d:Document)
                    WHERE u.username = $username
                    AND us.upload_session = $upload_session
                    AND d.session_file_id = $session_file_id
                SET
                    d.size_in_bytes = $size_in_bytes
                """
            result = tx.run(
                cypher,
                username=user.username,
                upload_session=upload_session,
                session_file_id=document.session_file_id,
                size_in_bytes=document.size_in_bytes,
            )
            summary = result.consume()
            if summary.counters.properties_set < 1:
                raise HTTPException(status_code=400, detail="Property was not set.")
            return document.session_file_id

        with self.driver.session() as session:
            session.execute_write(update_file_size_work)

        # link creation
        base_url = os.environ["KONTROLL_BASE_URL"] + "documents/1.0/"
        upload_session_url = "?upload_session=" + upload_session
        upload_complete_url = base_url + "upload-completion" + upload_session_url
        upload_cancellation_url = base_url + "upload-cancellation" + upload_session_url
        upload_completion = LinkData(url=upload_complete_url)
        upload_cancellation = LinkData(url=upload_cancellation_url)
        document_to_upload_model = DocumentToUpload(
            session_file_id=document.session_file_id,
            upload_file_parts=list(),
            upload_completion=upload_completion,
            upload_cancellation=upload_cancellation,
        )

        def add_part_work(tx) -> UUID:
            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:CONTAINS]->(d:Document)
                    WHERE u.username = $username
                    AND us.upload_session = $upload_session
                    AND d.session_file_id = $session_file_id
                CREATE (d)-[r3:HAS]->(p:Part)
                    SET p.number = $part_number,
                        p.uuid = $part_uuid,
                        p.content_range_start = $content_range_start,
                        p.content_range_end = $content_range_end,
                        p.content_length = $content_length
            """
            result = tx.run(
                cypher,
                username=user.username,
                upload_session=upload_session,
                session_file_id=document.session_file_id,
                part_number=part_number,
                part_uuid=str(upload_part_uuid),
                content_range_start=content_range_start,
                content_range_end=content_range_end,
                content_length=content_length,
            )

            summary = result.consume()
            if summary.counters.nodes_created != 1:
                raise HTTPException(status_code=400, detail="Part was not created.")
            return upload_part_uuid

        # calculate the number of file parts to send
        number_of_parts = math.ceil(int(document.size_in_bytes) / int(os.environ["SESSION_MAX_FILE_SIZE_BYTES"]))
        part_length = math.ceil(int(document.size_in_bytes) / number_of_parts)
        for part_number in range(number_of_parts):
            content_range_start = part_number * part_length
            content_range_end = ((part_number + 1) * part_length) - 1
            if content_range_end > document.size_in_bytes:
                content_range_end = document.size_in_bytes - 1
            content_length = content_range_end - content_range_start + 1
            upload_part_uuid = uuid4()
            upload_part_url = "upload-part/" + str(upload_part_uuid)
            additional_headers = {"values": [{"name": "Content-Length", "value": content_length}]}
            part_instruction = UploadFilePartInstruction(
                url=base_url + upload_part_url,
                http_method="POST",
                additional_headers=additional_headers,
                include_authorization=True,
                content_range_start=content_range_start,
                content_range_end=content_range_end,
            )

            with self.driver.session() as session:
                added_part = session.execute_write(add_part_work)

            if added_part == upload_part_uuid:
                document_to_upload_model.upload_file_parts.append(part_instruction)

        return document_to_upload_model

    def user_has_part(self, part_id: str, current_user: User) -> Union[Document, bool]:
        def user_has_part_work(tx) -> Union[Document, bool]:
            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:CONTAINS]->(d:Document)-[r3:HAS]->(p:Part)
                WHERE u.username = $username
                    AND p.uuid = $part_id
                RETURN d AS document
            """

            result = tx.run(cypher, username=current_user.username, part_id=part_id)

            first = result.single()
            if first is None:
                print("There were no parts in graph!")
                return False

            document_node = first.get("document")
            document = self.document_node_to_model(document_node)

            print("User had this part " + part_id + " in document id: " + document.document_id)
            return document

        with self.driver.session() as session:
            return session.execute_read(user_has_part_work)

    def mark_part_as_uploaded(self, part_id: str, current_user: User) -> bool:
        def mark_part_as_uploaded_work(tx) -> bool:
            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:CONTAINS]->(d:Document)-[r3:HAS]->(p:Part)
                WHERE u.username = $username
                    AND p.uuid = $part_id
                SET p.uploaded = True
            """

            result = tx.run(cypher, username=current_user.username, part_id=part_id)

            summary = result.consume()
            if summary.counters.properties_set < 1:
                raise HTTPException(status_code=400, detail="Part not marked as uploaded.")
            else:
                return True

        with self.driver.session() as session:
            return session.execute_write(mark_part_as_uploaded_work)

    def all_parts_uploaded(self, upload_session: str, current_user: User) -> bool:
        def check_uploaded_parts_work(tx) -> bool:
            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:CONTAINS]->(d:Document)-[r3:HAS]->(p:Part)
                WHERE u.username = $username
                    AND us.upload_session = $upload_session
                    AND p.uploaded IS NULL
                RETURN count(p) as parts
                """

            result = tx.run(cypher, username=current_user.username, upload_session=upload_session)

            first = result.single()
            if first is None:
                return False

            number_of_parts = first.get("parts")

            print("There are number of parts not uploaded: ", number_of_parts)

            if number_of_parts > 0:
                raise HTTPException(status_code=400, detail="All parts not uploaded.")
            else:
                return True

        with self.driver.session() as session:
            return session.execute_read(check_uploaded_parts_work)

    def retrieve_uploaded_parts(self, upload_session: str, current_user: User) -> list:
        def retrieve_uploaded_parts_work(tx) -> list:
            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:CONTAINS]->(d:Document)-[r3:HAS]->(p:Part)
                WHERE u.username = $username
                    AND us.upload_session = $upload_session
                    AND p.uploaded IS NOT NULL
                RETURN p as part
                ORDER BY part.number
            """
            results = tx.run(cypher, username=current_user.username, upload_session=upload_session)

            parts_list = list()
            for result in results:
                part_json = self.node_to_json(result.get("part"))
                parts_list.append(part_json["uuid"])
            return parts_list

        with self.driver.session() as session:
            return session.execute_read(retrieve_uploaded_parts_work)

    def get_document_from_session(self, upload_session: UUID, current_user: User) -> Document:
        def get_document_work(tx) -> Document:

            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:CONTAINS]->(d:Document)
                WHERE u.username = $username
                    AND us.upload_session = $upload_session
                RETURN d AS document
                """

            result = tx.run(cypher, username=current_user.username, upload_session=upload_session)

            first = result.single()
            document_node = first.get("document")
            return self.document_node_to_model(document_node)

        with self.driver.session() as session:
            return session.execute_read(get_document_work)

    def document_upload_finish(self, upload_session: UUID, current_user: User, project) -> bool:
        def upload_finish_work(tx):
            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:CONTAINS]->(d:Document)-[r3:HAS]->(part:Part)
                WHERE u.username = $username
                    AND us.upload_session = $upload_session
                    AND part.uploaded = True
                MATCH (proj:Project)
                WHERE
                    proj.project_id = $project
                DETACH DELETE part
                DELETE r2
                CREATE (proj)-[r4:CONTAINS]->(d)
            """
            result = tx.run(cypher, username=current_user.username, upload_session=upload_session, project=project)

            summary = result.consume()
            if summary.counters.nodes_deleted < 1:
                raise HTTPException(status_code=400, detail="Graph could not be upload finished.")
            else:
                return True

        with self.driver.session() as session:
            return session.execute_write(upload_finish_work)

    def get_upload_cancellation(self, upload_session: UUID, current_user: User) -> Union[Document, bool]:

        def retrieve_document_work(tx) -> Union[Document, bool]:
            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:CONTAINS]->(d:Document)
                WHERE u.username = $username
                    AND us.upload_session = $upload_session
                RETURN d as document
            """
            result = tx.run(cypher, username=current_user.username, upload_session=upload_session)

            first = result.single()
            if first is None:
                return False

            document_node = first.get("document")
            return self.document_node_to_model(document_node)

        def upload_cancellation_work(tx) -> bool:
            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Session:Upload)-[r2:CONTAINS]->(d:Document)-[r3:HAS]->(p:Part)
                WHERE u.username = $username
                    AND us.upload_session = $upload_session
                DETACH DELETE us, d, p
            """
            result = tx.run(cypher, username=current_user.username, upload_session=upload_session)

            summary = result.consume()
            if summary.counters.nodes_deleted < 1:
                raise HTTPException(status_code=400, detail="Any nodes could not be deleted.")
            else:
                return True

        with self.driver.session() as session:
            document = session.execute_read(retrieve_document_work)
            session.execute_write(upload_cancellation_work)
            return document

    # ---- DOWNLOAD FUNCTIONS ----

    def post_select_documents(
        self, select_documents: SelectDocuments, current_user: User
    ) -> DocumentDiscoverySessionInitialization:
        def post_select_documents_work(tx) -> DocumentDiscoverySessionInitialization:

            session_uuid = str(uuid4())
            session_callback_timedelta = int(select_documents.callback.expires_in)
            session_url_validity_timedelta = 10 + int(os.environ["SESSION_URL_VALIDITY_SECONDS"])
            if not hasattr(select_documents, "server_context") or not select_documents.server_context:
                select_documents.server_context = str(uuid4())

            cypher = """
                MATCH (u:User)
                WHERE u.username = $username
                CREATE (u)-[r1:HAS]->(s:Session:Select)-[r2:HAS]->(l:Link)
                WITH *
                CALL apoc.ttl.expireIn(s, $session_callback_timedelta, 's')
                CALL apoc.ttl.expireIn(l, $session_url_timedelta, 's')
                SET
                    s.server_context = $server_context,
                    s.selection_session = $selection_session,
                    s.callback = $callback,
                    s.session_url_timedelta = $session_url_timedelta,
                    s.session_callback_timedelta = $session_callback_timedelta
            """

            result = tx.run(
                cypher,
                username=current_user.username,
                session_callback_timedelta=session_callback_timedelta,
                session_url_timedelta=session_url_validity_timedelta,
                server_context=select_documents.server_context,
                selection_session=str(session_uuid),
                callback=select_documents.callback.url,
            )

            summary = result.consume()
            if summary.counters.nodes_created < 2:
                raise HTTPException(status_code=400, detail="Session or link node was not created.")

            session_init_dict = dict()
            session_init_dict["select_documents_url"] = (
                os.environ["KONTROLL_BASE_URL"]
                + "documents/1.0/"
                + "document-selection?selection_session="
                + session_uuid
            )
            session_init_dict["expires_in"] = os.environ["SESSION_URL_VALIDITY_SECONDS"]
            session_init_model = DocumentDiscoverySessionInitialization(**session_init_dict)

            return session_init_model

        with self.driver.session() as session:
            return session.execute_write(post_select_documents_work)

    def get_data_for_document_selection(self, selection_session: UUID) -> DataForDocumentSelection:
        def get_data_for_document_selection_work(tx) -> DataForDocumentSelection:
            # to get the projects
            cypher = """
                MATCH (l:Link)<-[r1:HAS]-(ss:Session:Select)<-[r2:HAS]-(u:User)-[r3:HAS_ACTIONS_ON]->(p:Project)
                WHERE ss.selection_session = $selection_session
                RETURN p AS project
                ORDER BY project.name
            """
            project_results = tx.run(cypher, selection_session=str(selection_session))

            project_list = list()
            for project_result in project_results:
                project_json = self.node_to_json(project_result.get("project"))
                project_json["documents"] = list()
                project_model = Project(**project_json)

                # to get the documents
                cypher = """
                    MATCH (l:Link)<-[r1:HAS]-(ss:Session:Select)<-[r2:HAS]-(u:User)-[r3:HAS_ACTIONS_ON]->(p:Project)-[r4:CONTAINS]->(d:Document)
                    WHERE ss.selection_session = $selection_session
                    AND p.project_id = $project_id
                    RETURN d AS document
                    ORDER BY d.title, d.version_index
                """
                document_results = tx.run(
                    cypher, selection_session=str(selection_session), project_id=str(project_model.project_id)
                )

                for document_result in document_results:
                    document_node = document_result.get("document")
                    document_model = self.document_node_to_model(document_node)
                    project_model.documents.append(document_model)

                project_list.append(project_model)

            # to get the user and some session data
            cypher = """
                   MATCH (u:User)-[r1:HAS]->(ss:Session:Select)-[r2:HAS]->(l:Link)
                   WHERE ss.selection_session = $selection_session
                   RETURN
                       ss.server_context AS server_context,
                       ss.callback AS callback,
                       ss.session_callback_timedelta AS session_callback_timedelta,
                       u AS user
                   """

            result = tx.run(cypher, selection_session=str(selection_session))

            first = result.single()
            if first is None:
                raise HTTPException(status_code=401, detail="No session or link.")

            user_node = first.get("user")
            user_dict = self.node_to_json(user_node)

            for_document_selection_dict = dict()
            for_document_selection_dict["server_context"] = first.get("server_context")

            callback_link = dict()
            callback_link["url"] = first.get("callback")
            callback_link["expires_in"] = first.get("session_callback_timedelta")

            for_document_selection_dict["callback"] = callback_link
            for_document_selection_dict["projects"] = project_list
            for_document_selection_dict["current_user"] = user_dict

            for_document_selection_model = DataForDocumentSelection(**for_document_selection_dict)

            print("Data for document selection: ", for_document_selection_dict)

            return for_document_selection_model

        with self.driver.session() as session:
            return session.execute_read(get_data_for_document_selection_work)

    def post_mark_documents_as_selected(
        self, all_documents: list, selection_session: UUID
    ) -> DocumentsMarkedAsSelected:

        def mark_documents_as_selected_work(tx) -> DocumentsMarkedAsSelected:
            cypher = """
                MATCH (ss:Session:Select)<-[r2:HAS]-(u:User)-[r3:HAS_ACTIONS_ON]->(p:Project)-[r4:CONTAINS]->(d:Document)
                WHERE ss.selection_session = $selection_session
                AND d.document_id = $document_id
                MERGE (ss)-[r5:SELECTED]->(d)
            """

            selected_documents_model = DocumentsMarkedAsSelected(documents=list())

            for document in all_documents:
                result = tx.run(cypher, selection_session=str(selection_session), document_id=str(document))

                summary = result.consume()

                if summary.counters.relationships_created > 0:
                    selected_documents_model.documents.append(document)

            return selected_documents_model

        with self.driver.session() as session:
            return session.execute_write(mark_documents_as_selected_work)

    @staticmethod
    def document_version_links(document_json):
        document_id = document_json["document_id"]
        version_index = document_json["version_index"]
        base = (
            os.environ["KONTROLL_BASE_URL"] + "documents/1.0/document/" + document_id + "/version/" + str(version_index)
        )
        return DocumentVersionLinks(
            document_version=LinkData(url=base),
            document_version_metadata=LinkData(url=base + "/metadata"),
            document_version_download=LinkData(url=base + "/download"),
            document_versions=LinkData(url=base + "/versions"),
            document_details=LinkData(url=base + "/details"),
        )

    def get_download_instructions(self, session_id: UUID, server_context: str, current_user: User) -> SelectedDocuments:
        def get_download_instructions_work(tx) -> SelectedDocuments:
            cypher = """
                 MATCH (ss:Session:Select)-[r1:SELECTED]->(d:Document)
                 WHERE ss.selection_session = $selection_session
                 RETURN d AS document
             """
            results = tx.run(cypher, selection_session=str(session_id))

            document_list = list()
            for result in results:
                document_node = result.get("document")
                document_model = self.document_node_to_model(document_node)
                document_list.append(document_model)

            selected_documents = SelectedDocuments(server_context=server_context, documents=document_list)
            return selected_documents

        with self.driver.session() as session:
            return session.execute_read(get_download_instructions_work)

    def get_upload_documents(self, upload_session: UUID, current_user: User) -> UploadDocuments:
        def get_upload_documents_work(tx) -> UploadDocuments:
            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Upload:Session)-[r2:HAS]->(l:Link),
                (us)-[r3:CONTAINS]->(d:Document:Temporary)
                WHERE u.username = $username
                AND us.upload_session = $upload_session
                RETURN d AS document
                """
            results = tx.run(cypher, username=current_user.username, upload_session=upload_session)
            file_list = list()
            for result in results:
                file_json = self.node_to_json(result.get("document"))
                file_model = FileToUpload(**file_json)
                file_list.append(file_model)

            cypher = """
                MATCH (u:User)-[r1:HAS]->(us:Upload:Session)-[r2:HAS]->(l:Link),
                WHERE u.username = $username
                AND us.upload_session = $upload_session
                RETURN
                    us.server_context AS server_context,
                    us.callback AS callback,
                    us.session_callback_timedelta
                """
            result = tx.run(cypher, username=current_user.username, upload_session=upload_session)

            callback = result.get("callback")
            session_callback_timedelta = result.get("session_callback_timedelta")

            upload_documents = UploadDocuments()
            upload_documents.server_context = result.get("server_context")
            upload_documents.callback.url = result.get("callback")
            upload_documents.callback.expires_in = 3500  # difference between now and timedelta
            upload_documents.files = file_list

            return upload_documents

        with self.driver.session() as session:
            return session.execute_read(get_upload_documents_work)

    def get_document_version(
        self, document_id: UUID, version_index: int, current_user: User
    ) -> Union[DocumentVersion, bool]:
        def get_document_version_work(tx) -> Union[DocumentVersion, bool]:

            if version_index is None or version_index is False or not isinstance(version_index, int):
                version_index_criteria = "AND d.version_index = $version_index"
            else:
                version_index_criteria = ""

            cypher = (
                """
                MATCH (u:User)-[r3:HAS_ACTIONS_ON]->(p:Project)-[r4:CONTAINS]->(d:Document)
                WHERE u.username = $username
                AND d.document_id = $document_id
                %s
                RETURN d AS document
                ORDER by d.version_index DESC
                LIMIT 1
            """
                % version_index_criteria
            )

            result = tx.run(
                cypher, username=current_user.username, document_id=document_id, version_index=version_index
            )

            first = result.single()
            if first is None:
                print("There were no such document version.")
                return False

            document_node = first.get("document")
            return self.document_node_to_model(document_node)

        with self.driver.session() as session:
            return session.execute_read(get_document_version_work)

    def get_document_version_metadata(self, document_id, version_index, current_user) -> DocumentMetadataEntries:
        def get_document_version_metadata_work(tx) -> DocumentMetadataEntries:

            if version_index is None or version_index is False or not isinstance(version_index, int):
                version_index_criteria = "AND d.version_index = $version_index"
            else:
                version_index_criteria = ""

            cypher = (
                """
                MATCH (u:User)-[r3:HAS_ACTIONS_ON]->(p:Project)-[r4:CONTAINS]->(d:Document)
                WHERE u.username = $username
                AND d.document_id = $document_id
                %s
                RETURN d AS document
                ORDER by d.version_index DESC
                LIMIT 1
            """
                % version_index_criteria
            )

            result = tx.run(
                cypher, username=current_user.username, document_id=document_id, version_index=version_index
            )

            first = result.single()
            if first is None:
                print("There were no such document version.")
                return False

            document_json = self.node_to_json(first.get("document"))
            document_json["creation_date"] = self.bcf_time(document_json["creation_date"])
            metadata = ["title", "version_number", "creation_date"]
            entries = list()
            for each_metadata in metadata:
                each_metadata_text = each_metadata.replace("_", " ")
                each_metadata_text = each_metadata_text.capitalize()
                entry = {
                    "name": each_metadata_text,
                    "value": [document_json[each_metadata]],
                    "data_type": DataType.string,
                }
                entries.append(entry)
            return DocumentMetadataEntries(metadata=entries)

        with self.driver.session() as session:
            return session.execute_read(get_document_version_metadata_work)

    def get_document_versions(self, document_id, current_user) -> DocumentVersions:
        def get_document_versions_work(tx) -> DocumentVersions:
            cypher = """
                MATCH (u:User)-[r3:HAS_ACTIONS_ON]->(p:Project)-[r4:CONTAINS]->(d:Document)
                WHERE u.username = $username
                AND d.document_id = $document_id
                RETURN d AS document
            """
            results = tx.run(cypher, username=current_user.username, document_id=document_id)
            document_versions = DocumentVersions(documents=list())
            for result in results:
                document_json = self.node_to_json(result.get("document"))
                document_version = self.get_document_version(document_id, document_json["version_index"], current_user)
                document_versions.documents.append(document_version)
            return document_versions

        with self.driver.session() as session:
            return session.execute_read(get_document_versions_work)


doc_db = DOCDB(driver)
