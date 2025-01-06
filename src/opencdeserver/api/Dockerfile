FROM python:3.10-bullseye AS base
RUN apt-get update && apt-get install -y \
  unzip \
  && rm -rf /var/lib/apt/lists/* \
COPY ./app/ifcopenshell/ifcopenshell.zip /ifcopenshell.zip
CMD ["unzip", "/ifcopenshell.zip", "-d", "/usr/local/lib/python3.10/site-packages/"]
WORKDIR /code/app
COPY ./app/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install neo4j==5.9.0 uvicorn ifcopenshell Jinja2 python-multipart bcrypt --upgrade
# pip install: Install packages.
# --no-cache-dir: You can shrink the image size by disabling the cache.
# --upgrade: Upgrade packages.
# -r: use requirements file.
COPY ./app /code/app

FROM base AS server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers",  \
    "--ssl-keyfile", "/etc/letsencrypt/live/kontroll.digital/privkey.pem",  \
    "--ssl-certfile", "/etc/letsencrypt/live/kontroll.digital/fullchain.pem"]
# If running behind a proxy like Nginx or Traefik add --proxy-headers.
# --ssl-keyfile: Path to keyfile.
# --ssl-certificat: Path to certificate.