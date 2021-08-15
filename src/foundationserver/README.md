# Server-Test

```
$ pip install -r requirements.txt
$ cd bcfserver/
$ python
>>> from run import db
>>> db.create_all()
$ export FLASK_APP=run.py
$ flask run
```

Go to [http://localhost:5000](http://localhost:5000) to see the server

# Register the user

1. Go to http://localhost:5000/register to register the user
2. Create the client
3. For grant type enter authorization_code
4. For response_type enter code secret
5. Enter the scope and create the client

### You will be redirected to the page with the details of your client id and secret

# Foundation API

- Set the Base URL will be `http://127.0.0.1:5000/`
