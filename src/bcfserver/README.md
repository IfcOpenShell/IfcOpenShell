# Server-Test

1. Set up the server by installing the dependencies

2. Cd to the server directory i.e `cd IfcOpenShell\src\bcfserver`
3. Run `pip install -r requirements.txt` to install the dependencies

4. In Python Shell, do the following

   - `from bcfserver import db`
   - `db.create_all()` to create the database

5. Run `flask run` to start the server

Go to [http://localhost:5000](http://localhost:5000) to see the server in action.

# Register the user

1. Go to [http://localhost:5000/register](http://localhost:5000/register) to register the user
2. Create the client
3. For `grant type` enter `authorization_code`
4. For `response_type` enter `code secret`
5. Enter the scope and create the client

### You will be redirected to the page with the details of your client id and secret

# Foundation API

In foundation api, set base URL as `http://127.0.0.1:5000/` .
