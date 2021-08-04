# Server-Test

## Set up the server by installing the dependencies

### run `pip install -r requirements.txt` to install the dependencies

#### setup the database by running `db.create_all()` in python shell by importing db from website

### run `set FLASK_APP=app.py` to set the environment variable

### run `flask run` to start the server

### Go to [http://localhost:5000](http://localhost:5000) to see the server

# Register the user

#### Go to [http://localhost:5000/register](http://localhost:5000/register) to register the user

# Create the client

#### For `grant type` enter `authorization_code`

#### For `response_type` enter `code secret`

### Enter the scope and create the client

### You will be redirected to the page with the details of your client id and secret

### Use the bcf/v3/api.py to get the access token

#### For authentication endpoint use `http://localhost:5000/oauth/authorize`

### For token endpoint use `http://localhost:5000/oauth/token`

### Base URL will be `http://localhost:5000/`
