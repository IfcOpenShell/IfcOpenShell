#!/bin/bash
docker stop kontroll_fastapi
docker rm -v kontroll_fastapi
docker image rm kontroll_fastapi:latest
docker-compose up -d
docker logs kontroll_fastapi --follow
