import jsonpickle
import os
import pytz

from dateutil import parser
from uuid import uuid4, UUID

from neo4j import GraphDatabase

from datetime import datetime, timezone

from models.request import UserInDB
from security.secrets import get_secrets

get_secrets()

# neo4j://127.0.0.1:27687 is used when there are no environment variables, i.e. when running from terminal.
# otherwise the environment variable will have a value of neo4j://kontroll_neo4j:27687
# kontroll_neo4j is the docker-compose network.

driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_INITIAL_PASSWORD"])
)

# initial password should be changed to secret password

driver.verify_connectivity()

cypher_file_path = "./db_config/init.cypher"


class MyDB:

    def __init__(self, object_driver):
        self.driver = object_driver
        self.database = "neo4j"

    @staticmethod
    def timestamp():
        return datetime.now(timezone.utc).isoformat(sep="T", timespec="milliseconds")

    @staticmethod
    def bcf_time(any_datetime):
        if isinstance(any_datetime, str):
            datetime_any = parser.parse(any_datetime).astimezone(pytz.utc)
        elif isinstance(any_datetime, type(datetime.now())):
            datetime_any = any_datetime.astimezone(pytz.utc)
        else:
            return False
        string_date = datetime_any.isoformat(sep="T", timespec="milliseconds")
        return str(string_date)

    @staticmethod
    def safe_path(path_name):
        safe_path_name = "".join(x for x in path_name if x.isalnum() or "-")
        return safe_path_name

    @staticmethod
    def debug(endpoint: str, request, response):
        print(
            "\n\n\nEndpoint: ",
            jsonpickle.dumps(endpoint),
            "\nRequest: ",
            jsonpickle.dumps(request),
            "\nResponse: ",
            jsonpickle.dumps(response),
        )

    @staticmethod
    def node_to_json(node):
        json = {}
        for fields in node.items():
            json[fields[0]] = fields[1]
        return json

    @staticmethod
    def is_valid_uuid(uuid_to_test, version=4):
        try:
            uuid_obj = UUID(uuid_to_test, version=version)
        except ValueError:
            return False
        return str(uuid_obj) == uuid_to_test

    @staticmethod
    def new_uuid():
        try:
            uuid_obj = uuid4()
        except ValueError:
            return False
        return str(uuid_obj)

    def initialize_db(self):
        def initialize_db_work(tx):
            cypher_file = open(cypher_file_path, "r")
            cypher_data = cypher_file.read()
            cypher_file.close()
            cypher_statements = cypher_data.split(";")
            cypher_statements.pop()
            for cypher_statement in cypher_statements:
                tx.run(cypher_statement)
            return

        with self.driver.session() as session:
            return session.execute_write(initialize_db_work)

    def get_user(self, username: str):
        def get_user_work(tx, username_work: str):
            cypher = """
                MATCH (u:User)
                WHERE u.username = $username
                RETURN u AS user
                LIMIT 1
                """
            result = tx.run(cypher, username=username_work)
            first = result.single()
            if first is None:
                return None
            user_node = first.get("user")
            user_dict = self.node_to_json(user_node)
            user = UserInDB(**user_dict)
            return user

        with self.driver.session() as session:
            return session.execute_read(get_user_work, username_work=username)


db = MyDB(driver)
db.initialize_db()
