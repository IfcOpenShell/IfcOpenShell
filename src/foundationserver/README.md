# Server-Test

1. Cd to the server directory i.e cd `IfcOpenShell\src\bcfserver`

2. Set up the server by installing the dependencies

3. Run `pip install -r requirements.txt` to install the dependencies

4. In Python Shell, do the following

   - from run import db
   - db.create_all() to setup the database table

5. Run `set FLASK_APP=run.py`
6. Run `flask run` to start the server
7. Go to [http://localhost:5000](http://localhost:5000) to see the server

# Register the user

1. Go to http://localhost:5000/register to register the user
2. Create the client
3. For grant type enter authorization_code
4. For response_type enter code secret
5. Enter the scope and create the client

### You will be redirected to the page with the details of your client id and secret

# Foundation API

- Set the Base URL will be `http://127.0.0.1:5000/`
