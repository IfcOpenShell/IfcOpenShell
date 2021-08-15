from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


app = Flask(__name__)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
app.config["SECRET_KEY"] = "f613729206685405cde0e388"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite.db"
login_manager.login_view = "foundation_obj.login_page"
login_manager.login_message_category = "info"

from foundation.routes import foundation_obj
from bcf.routes import bcf


app.register_blueprint(foundation_obj)
app.register_blueprint(bcf)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
