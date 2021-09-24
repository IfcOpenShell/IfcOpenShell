
# OpenCDE - OpenCDE Python implementation
# Copyright (C) 2021 Prabhat Singh <singh01prabhat@gmail.com>
#
# This file is part of OpenCDE.
#
# OpenCDE is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenCDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with OpenCDE.  If not, see <http://www.gnu.org/licenses/>.

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
