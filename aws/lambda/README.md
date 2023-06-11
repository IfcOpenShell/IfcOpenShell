Dockerized AWS Lambda Function with Python and IfcOpenShell
===========================================================

This guide provides a Dockerfile and sample code to help you run an AWS Lambda function written in Python and utilizing IfcOpenShell library. 

> Note: This is a superficial guideline, in order to make this work for your usecase you will need a good understanding of other AWS services like SQS, S3, API Gateway etc.

Prerequisites
-------------

Make sure you have Docker installed on your machine. You can download Docker from the official website: [Docker Instalation](https://docs.docker.com/engine/install/)

Getting Started
---------------

1. **Clone this repository to your local machine:**

2. **Customize the Lambda function code:**
   
   - Replace the sample Lambda function code in the `example_handler` directory with your own code.
   - Update the import path in the Dockerfile's `CMD` instruction to match your Lambda function's handler function.

3. **Install the required Python packages:**
   - Edit the `requirements.txt` file and add any additional dependencies required by your Lambda function.

4. **Build the Docker image:**

   ```shell
   $ docker build -t lambda-ifcopenshell .
   ```

5. **Run the Docker container:**

    ```shell
   $ docker run lambda-ifcopenshell
    ```
6. **Test lambda locally**
    
    Follow the steps in this [guide](https://docs.aws.amazon.com/lambda/latest/dg/images-test.html)


7. **Deploy to lambda**
 
    This is beyond the scope of this example. Please refer to AWS documentation. Some tools that could be useful are - AWS CloudFormaton, AWS CDK, pulumi or terraform
