from flask import Flask
from flask import render_template
from flask import request
from flask import redirect

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_security import Security
from flask_security import SQLAlchemyUserDatastore
from flask_security import RoleMixin, UserMixin
from flask_security import current_user, login_required
from flask_security.forms import RegisterForm, LoginForm

from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired
from flask_wtf import FlaskForm
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = ''
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = ''
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = 'username'
app.config['SECUIRTY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_REGISTER_USER_TEMPLATE'] = 'login_user.html'
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'register_user.html'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), unique = True, nullable = False)
    description = db.Column(db.String(2000), unique = False, nullable = False)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(200), unique = True, nullable = False)
    password = db.Column(db.String(200), unique = False, nullable = False)
    name = db.Column(db.String(200), unique = False, nullable = False)
    username = db.Column(db.String(200), unique = True, nullable = False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary = roles_users, backref=db.backref('users', lazy='dynamic'))
    posts = db.relationship('Post', backref='user', lazy='dynamic')

class ExtendedRegisterForm(RegisterForm):
    name = StringField('Name')
    username = StringField('Username')

class ExtendedLoginForm(LoginForm):
    email = StringField('Username', [InputRequired()])

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')