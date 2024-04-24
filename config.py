from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_mail import Mail


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI","sqlite:///Spending.db")
db = SQLAlchemy()
db.init_app(app)


CORS(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get("email")
app.config['MAIL_PASSWORD'] = os.environ.get("password")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


app.config['SECRET_KEY'] = os.environ.get("flask_key")

app.config["JWT_SECRET_KEY"] = os.environ.get("WT-Key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
jwt = JWTManager(app)

mail = Mail(app)
