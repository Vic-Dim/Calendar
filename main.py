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
app.config['SECRET_KEY'] = 'Wheresoever you go, go with all your heart.'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'Pain breeds weakness.'
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = 'username'
app.config['SECUIRTY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_REGISTER_USER_TEMPLATE'] = 'security/register_user.html'
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'security/login_user.html'

# For more useful resources: https://flask-security-too.readthedocs.io/_/downloads/en/stable/pdf/

db = SQLAlchemy(app)
migrate = Migrate(app, db)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(300), unique = True, nullable = False)
    description = db.Column(db.String(3000), unique = False, nullable = False)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key = True)
    email = db.Column(db.String(300), unique = True, nullable = False)
    password = db.Column(db.String(300), unique = False, nullable = False)
    name = db.Column(db.String(300), unique = False, nullable = False)
    username = db.Column(db.String(300), unique = True, nullable = False)
    sex = db.Column(db.String(10), unique = False, nullable = False)
    age = db.Column(db.Integer(), unique = False, nullable = False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary = roles_users, backref=db.backref('users', lazy='dynamic'))
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    groups = db.relationship('Group', backref='user', lazy='dynamic')

class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer(), primary_key = True)
    group_name = db.Column(db.String(300))
    group_description = db.Column(db.String(3000))
    date_created = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    admin_id = db.Column(db.Integer(), db.ForeignKey('admin.id'))

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer(), primary_key = True)
    content = db.Column(db.String(300), unique = False, nullable = False)
    date_created = db.Column(db.DateTime())
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    group_id = db.Column(db.Integer(), db.ForeignKey('group.id'))

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer(), primary_key = True)
    content = db.Column(db.String, unique = False, nullable = False)
    date_created = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))
    group_id = db.Column(db.Integer(), db.ForeignKey('group.id'))

class New_Group(FlaskForm):
    group_name = StringField('Title')
    group_description = StringField('Description')

class New_Post(FlaskForm):
    content = TextAreaField('Content')

class New_Comment(FlaskForm):
    content = TextAreaField('Comment')

class ExtendRegisterForm(RegisterForm):
    name = StringField('Name')
    username = StringField('Username')

class ExtendLoginForm(LoginForm):
    email = StringField('Username', [InputRequired()])

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_form=ExtendRegisterForm, login_form=ExtendLoginForm)

@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')