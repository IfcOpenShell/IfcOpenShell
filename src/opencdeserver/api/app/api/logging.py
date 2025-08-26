from fastapi import FastAPI, APIRouter, Response, Request
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse
from fastapi.routing import APIRoute
from starlette.types import Message
from typing import Callable
import logging
import httpx


def log_info(req_body, res_body, route_url):
    logging.info("request:" + route_url + ":" + str(req_body))
    logging.info("response:" + route_url + ":" + str(res_body))


class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            req_body = await request.body()
            response = await original_route_handler(request)
            route_url = str(request.url)
            if isinstance(response, StreamingResponse):
                res_body = b""
                async for item in response.body_iterator:
                    res_body += item
                task = BackgroundTask(log_info, req_body, res_body, route_url)
                return Response(
                    content=res_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                    background=task,
                )
            else:
                if hasattr(response, "body"):
                    res_body = response.body
                else:
                    res_body = {"no response": True}
                response.background = BackgroundTask(log_info, req_body, res_body, route_url)
                return response

        return custom_route_handler


logging.basicConfig(filename="logs/info.log", level=logging.DEBUG)
