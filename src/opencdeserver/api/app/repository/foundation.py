import os
import hashlib

from datetime import timedelta

from fastapi import HTTPException

from database.neo4j import MyDB, driver
from security.secure import create_access_token
from jose import jwt

from security.secrets import get_secrets
from security.secure import credentials_exception

from models.foundation_other import *
from models.other import *

secrets = get_secrets()


class FoundationDB(MyDB):

    # implemented
    def create_authorization_code(self, username, authorization_code, scope) -> bool:
        def create_authorization_code_work(tx) -> bool:
            cypher = """
                    MATCH (u:User)
                    WHERE u.username = $username
                    OPTIONAL MATCH (u)-[r1:CAN_USE]->(t:Token)
                    WITH u, t
                    DETACH DELETE t
                    MERGE (u)-[r:CAN_USE]->(ac:AuthorizationCode)
                    SET ac.code = $authorization_code
                    SET ac.scope = $scope
                    WITH ac
                    CALL apoc.ttl.expireIn(ac, $time_delta, 's')
                    RETURN ac AS authorization_code
                    """
            result = tx.run(
                cypher,
                username=username,
                authorization_code=authorization_code,
                scope=scope,
                time_delta=int(os.environ["SECURITY_AUTHORIZATION_CODE_EXPIRE_SECONDS"]),
            )
            summary = result.consume()
            if summary.counters.nodes_created < 1:
                raise HTTPException(status_code=400, detail="Authorization code was not created.")
            return summary.counters.nodes_created

        with self.driver.session() as session:
            return session.execute_write(create_authorization_code_work)

    def use_authorization_code(self, authorization_code) -> TokenInfo:
        def use_code_to_get_user_info_work(tx) -> TokenData:
            cypher = """
                        MATCH (u:User)-[r1:CAN_USE]->(ac:AuthorizationCode)
                        WHERE ac.code = $authorization_code
                        WITH u.username AS username, ac.scope AS scope
                        RETURN
                            username, scope
                        """
            result = tx.run(cypher, authorization_code=authorization_code)
            first = result.single()
            if first is None:
                raise HTTPException(status_code=404, detail="Authorization code not found.")
            authorized_user = TokenData()
            authorized_user.username = first.get("username")
            authorized_user.scopes = first.get("scope").split(" ")
            return authorized_user

        with self.driver.session() as session:
            user_info = session.execute_read(use_code_to_get_user_info_work)

        token_info = TokenInfo()
        token_info.access_token = create_access_token(
            user_info.dict(), timedelta(seconds=int(os.environ["SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS"]))
        )
        token_info.refresh_token = create_access_token(
            user_info.dict(), timedelta(seconds=int(os.environ["SECURITY_REFRESH_TOKEN_EXPIRE_SECONDS"]))
        )

        def add_tokens_and_delete_code_work(tx) -> bool:
            cypher = """
                            MATCH (u:User)-[r1:CAN_USE]->(ac1:AuthorizationCode)
                            WHERE ac1.code = $authorization_code
                            AND u.username = $username
                            DETACH DELETE ac1
                            MERGE (u)-[r4:CAN_USE]->(t2:Token:AccessToken)
                            SET t2.value = $access_token
                            SET t2.hash = $access_token_hash
                            MERGE (u)-[r5:CAN_USE]->(t3:Token:RefreshToken)
                            SET t3.value = $refresh_token
                            SET t3.hash = $refresh_token_hash
                            """
            result = tx.run(
                cypher,
                authorization_code=authorization_code,
                username=user_info.username,
                access_token=token_info.access_token,
                access_token_hash=hashlib.md5(token_info.access_token.encode("utf-8")).hexdigest(),
                refresh_token=token_info.refresh_token,
                refresh_token_hash=hashlib.md5(token_info.refresh_token.encode("utf-8")).hexdigest(),
            )

            summary = result.consume()
            if summary.counters.nodes_created < 1 or summary.counters.nodes_deleted < 1:
                raise HTTPException(status_code=400, detail="Tokens were not created.")
            return summary.counters.nodes_created

        with self.driver.session() as session:
            session.execute_write(add_tokens_and_delete_code_work)

        return token_info

    def use_refresh_token(self, refresh_token) -> TokenInfo:
        def use_refresh_to_get_access_work(tx) -> (TokenData, TokenInfo):
            cypher = """
                        MATCH (rt:RefreshToken)<-[r1:CAN_USE]-(u:User)-[r2:CAN_USE]->(at:AccessToken)
                        WHERE u.username = $username
                        AND rt.hash = $refresh_token_hash
                        RETURN
                            at.value AS access_token
                        """
            refresh_token_payload = jwt.decode(
                refresh_token, secrets["security_secret_key"], algorithms=[os.environ["SECURITY_ALGORITHM"]]
            )
            username_from_refresh_token: str = refresh_token_payload.get("username")
            print("refresh_token_username: ", username_from_refresh_token)
            result = tx.run(
                cypher,
                username=username_from_refresh_token,
                refresh_token_hash=hashlib.md5(refresh_token.encode("utf-8")).hexdigest(),
            )
            first = result.single()
            if first is None:
                raise HTTPException(status_code=404, detail="Access token not found.")
            token_info = TokenInfo()
            token_info.access_token = first.get("access_token")
            token_info.refresh_token = refresh_token
            access_token_payload = jwt.decode(
                token_info.access_token, secrets["security_secret_key"], algorithms=[os.environ["SECURITY_ALGORITHM"]]
            )
            username_from_access_token: str = access_token_payload.get("username")
            if username_from_access_token is None:
                raise credentials_exception
            token_scopes = access_token_payload.get("scopes", [])
            token_data = TokenData(scopes=token_scopes, username=username_from_access_token)
            return token_data, token_info

        with self.driver.session() as session:
            got_token_data, got_token_info = session.execute_read(use_refresh_to_get_access_work)
        new_token_info = TokenInfo()
        new_token_info.access_token = create_access_token(
            got_token_data.dict(), timedelta(seconds=int(os.environ["SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS"]))
        )
        new_token_info.refresh_token = create_access_token(
            got_token_data.dict(), timedelta(seconds=int(os.environ["SECURITY_REFRESH_TOKEN_EXPIRE_SECONDS"]))
        )

        def update_tokens_work(tx) -> bool:
            cypher = """
                    MATCH (u:User)
                    WHERE u.username = $username
                    OPTIONAL MATCH (u)-[r1:CAN_USE]->(t:Token)
                    WITH u, t
                    DETACH DELETE t
                    MERGE (rt:Token:RefreshToken)<-[r2:CAN_USE]-(u)-[r3:CAN_USE]->(at:Token:AccessToken)
                    SET
                        rt.value = $refresh_token,
                        at.value = $access_token,
                        rt.hash = $refresh_token_hash,
                        at.hash = $access_token_hash
                """
            result = tx.run(
                cypher,
                username=got_token_data.username,
                access_token=new_token_info.access_token,
                refresh_token=new_token_info.refresh_token,
                access_token_hash=hashlib.md5(new_token_info.access_token.encode("utf-8")).hexdigest(),
                refresh_token_hash=hashlib.md5(new_token_info.refresh_token.encode("utf-8")).hexdigest(),
            )
            summary = result.consume()
            if summary.counters.nodes_created < 2 or summary.counters.nodes_deleted < 2:
                raise HTTPException(status_code=400, detail="Tokens were not deleted and created.")
            return summary.counters.nodes_created

        with self.driver.session() as session:
            session.execute_write(update_tokens_work)
        return new_token_info


foundation_db = FoundationDB(driver)
