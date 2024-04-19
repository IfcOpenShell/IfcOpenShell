# Dockerfile for Running AWS Lambda Function with Python and IfcOpenShell

# Base image: Python 3.9 from AWS's public container registry
FROM public.ecr.aws/docker/library/python:3.9 AS build

# Set the location of your Lambda function code
ARG FUNCTION_DIR="/var/task"

# Install necessary packages
RUN apt-get -y update && apt-get -y install unzip curl

# Install AWS Lambda runtime interface client
RUN pip install --target ${FUNCTION_DIR} awslambdaric

# Set the IfcOpenShell build version (check available builds at: https://docs.ifcopenshell.org/ifcopenshell-python/installation.html)
ARG IFC_OPENSHELL_BUILD="39-v0.7.0-476ab50"

# Download and extract IfcOpenShell
RUN curl https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-${IFC_OPENSHELL_BUILD}-linux64.zip -O && \
    unzip ifcopenshell-python-${IFC_OPENSHELL_BUILD}-linux64.zip && \
    mv ifcopenshell ${FUNCTION_DIR} && \
    rm ifcopenshell-python-${IFC_OPENSHELL_BUILD}-linux64.zip

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Lambda function code
COPY ./example_handler ${FUNCTION_DIR}/example_handler

# Set the working directory
WORKDIR ${FUNCTION_DIR}

# Set the entrypoint for the Lambda function
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

# Set the Python import path to the Lambda function handler
# This path is relative to the root of the Lambda function code (FUNCTION_DIR)
# Lambda invocation will look for this path
CMD ["example_handler.extract_wall_psets_handler"]
