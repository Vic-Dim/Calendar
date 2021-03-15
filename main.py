from flask import Flask, render_template
from flask import request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_security import Security
from flask_security import SQLAlchemyUserDatastore
from flask_security import RoleMixin, UserMixin
from flask_security import current_user, login_required
from flask_security.forms import RegisterForm, LoginForm

from wtforms import StringField, TextAreaField, SelectField
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
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_REGISTER_USER_TEMPLATE'] = 'security/register_user.html'
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'security/login_user.html'

# For more useful resources: https://flask-security-too.readthedocs.io/_/downloads/en/stable/pdf/


db = SQLAlchemy(app)
migrate = Migrate(app, db)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

groups_users = db.Table('groups_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer(), db.ForeignKey('group.id')))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(300), unique=True, nullable=False)
    description = db.Column(db.String(3000), unique=False, nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(300), unique=True, nullable=False)
    password = db.Column(db.String(300), unique=False, nullable=False)
    name = db.Column(db.String(300), unique=False, nullable=False)
    username = db.Column(db.String(300), unique=True, nullable=False)
    age = db.Column(db.Integer(), unique=False, nullable=False)
    sex = db.Column(db.String(30), unique=False, nullable=False)
    status = db.Column(db.String(30), unique=False, nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime(), default = datetime.now())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    groups = db.relationship('Group', secondary=groups_users, backref=db.backref('users', lazy='dynamic'))
    posts = db.relationship('Post', backref='post', lazy='dynamic')
    comments = db.relationship('Comment', backref='comment', lazy='dynamic')

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
    email = db.Column(db.String(300), unique=True, nullable=False)
    password = db.Column(db.String(300), unique=False, nullable=False)
    name = db.Column(db.String(300), unique=False, nullable=False)
    username = db.Column(db.String(300), unique=True, nullable=False)
    age = db.Column(db.Integer(), unique=False, nullable=False)
    sex = db.Column(db.String(30), unique=False, nullable=False)
    status = db.Column(db.String(30), unique=False, nullable=False)
    confirmed_at = db.Column(db.DateTime(), default = datetime.now())
    groups = db.relationship('Group', backref='group', lazy='dynamic')

    def __init__(self, id, email, password, name, username, age, sex, status, confirmed_at):
        self.id = id
        self.email = email
        self.password = password
        self.name = name
        self.username = username
        self.age = age
        self.sex = sex
        self.status = status
        self.confirmed_at = confirmed_at

class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(300))
    description = db.Column(db.String(3000))
    date_created = db.Column(db.DateTime())
    admin_id = db.Column(db.Integer(), db.ForeignKey('admin.id'))
    posts = db.relationship('Post', backref='group', lazy='dynamic')

   
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer(), primary_key = True)
    content = db.Column(db.String(300), unique = False, nullable = False)
    date_created = db.Column(db.DateTime())
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer(), db.ForeignKey('group.id'))

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer(), primary_key = True)
    content = db.Column(db.String, unique = False, nullable = False)
    date_created = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))

class Apply(db.Model):
	__tablename__ = 'apply'
	id = db.Column(db.Integer(), primary_key = True)
	content = db.Column(db.String(1000), unique = False, nullable = False)
	user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	admin_id = db.Column(db.Integer(), db.ForeignKey('admin.id'))


class New_Group(FlaskForm):
    name = StringField('Title')
    description = StringField('Description')

class New_Post(FlaskForm):
    content = TextAreaField('Content')

class New_Comment(FlaskForm):
    content = TextAreaField('Content')


class ExtendRegisterForm(RegisterForm):
    name = StringField('Name')
    username = StringField('Username')
    age = StringField("Age")
    sex = SelectField("Sex", choices=[('Male', 'Male'), ('Female', 'Female')])
    status = SelectField("Status", choices=[('School Student', 'School Student'), 
                                            ('High School Student', 'High School Student'),
                                            ('College Student', 'College Student'),
                                            ('Employed Graduated Student', 'Employed Graduated Student'), 
                                            ('Unemployed Graduated Student', 'Unemployed Graduated Student')])

class ExtendLoginForm(LoginForm):
    email = StringField('Username', [InputRequired()])


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_form=ExtendRegisterForm, login_form=ExtendLoginForm)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html', current_user=current_user)

@app.route('/invitations', methods=['GET', 'POST'])
@login_required
def invitations():
    return render_template('invitations.html', current_user=current_user)

@app.route('/all_groups', methods=['GET', 'POST'])
def all_groups():

    form = New_Group()

    if request.method == 'POST' and form.validate_on_submit():
        new_group = Group(name=form.name.data, description=form.description.data, date_created=datetime.now())
        new_admin = Admin(current_user.id, current_user.email, current_user.password, current_user.name, current_user.username,
                            current_user.age, current_user.sex, current_user.status, current_user.confirmed_at)
        new_group.admin_id = new_admin.id
        db.session.add(new_group)
        db.session.commit()
        
        admin = Admin.query.get(int(new_admin.id))

        if admin != None:
            admin.groups.append(new_group)
        else:
            db.session.add(new_admin)
            db.session.commit()
            new_admin.groups.append(new_group)

    groups = Group.query.all()
    return render_template('all_groups.html', form=form, groups=groups, current_user=current_user)

@app.route('/group/<group_id>', methods=['GET', 'POST'])
def group(group_id):
    form = New_Post()
    group = Group.query.get(int(group_id))

    if request.method == 'POST' and form.validate_on_submit():
        try:
            post = Post(user_id=current_user.id, content = form.content.data, date_created=datetime.now())
            group.posts.append(post)
            db.session.commit()
        except:
            return "There was a problem adding a new post on this topic!"

    posts = Post.query.filter_by(group_id=group_id).all()
    users = group.users
    return render_template('group.html', group=group, form=form, posts=posts, users=users, current_user=current_user)

@app.route('/post/<post_id>', methods=['GET', 'POST'])
def post(post_id):
	post = Post.query.get(int(post_id))

	if request.method == 'POST':
		try:
			new_comment = Comment(content=request.form['new_content'], date_created=datetime.now(), user_id=current_user.id, post_id=post.id)
			post.comments.append(new_comment)
			db.session.commit()
		except:
			return "There was a problem adding a new comment on this post!"			

		return redirect(request.referrer)

	else:
		comments = Comment.query.filter_by(post_id=post_id).all()
		return render_template('post.html', post=post, comments=comments, current_user=current_user)


@app.route('/apply_for_group/<group_id>', methods = ['GET', 'POST'])
def apply_for_group(group_id):
	group = Group.query.get(int(group_id))
	
	if request.method == 'POST':
		
		admin = Admin.query.filter_by(id=group.admin_id).first()
		
		appliance = Apply(content=request.form['appliance_content'], user_id=current_user.id, admin_id=admin.id)
		db.session.add(appliance)
		db.session.commit()
	
		return redirect(request.referrer)
	
	else:
		return render_template('apply_for_group.html', current_user=current_user, group=group)
		
@app.route('/join_requests')
def join_requests():		
	
	appliances = Apply.query.filter_by(admin_id = current_user.id).all()
	
	return render_template('join_requests.html', appliances=appliances)	

@app.route('/apply/<apply_id>', methods = ['POST', 'GET'])
def apply(apply_id):
	
	appliance = Apply.query.get(int(apply_id))
	content = appliance.content
	user = User.query.filter_by(id=appliance.user_id).first()	
	admin = Admin.query.filter_by(id=appliance.admin_id).first()
	
	if request.method == 'POST':
		
		answer = request.form.getlist('answer')
		group = Group.query.filter_by(admin_id=admin.id).first()
	
		if answer == "Yes" and group not in user.groups:
			user.groups.append(group)
	
		db.session.delete(appliance)
		db.session.commit()
	
		return redirect(request.referrer)
	
	else:
		return render_template('apply.html', content=Apply.query.get(int(apply_id)).content, user=user, apply_id=apply_id)

@app.route('/update_group/<group_id>', methods = ['POST', 'GET'])
def update_group(group_id):
	group = Group.query.get(int(group_id))
		
	if request.method == 'POST':	
		
		new_title = request.form['new_title']
		new_content = request.form['new_content']
		group.name = new_title
		group.description = new_content	
	
		db.session.commit()
	
		return redirect(request.referrer)
	
	else:
		return render_template('update_group.html', group=group)	
	
@app.route('/update_post/<post_id>', methods = ['POST', 'GET'])
def update_post(post_id):
	post = Post.query.get(int(post_id))
		
	if request.method == 'POST':	
		
		new_content = request.form['new_content']
		post.content = new_content	
	
		db.session.commit()
	
		return redirect(request.referrer)
	
	else:
		return render_template('update_post.html', post=post)	

@app.route('/update_comment/<comment_id>', methods = ['POST', 'GET'])
def update_comment(comment_id):
	comment = Comment.query.get(int(comment_id))
		
	if request.method == 'POST':	
		
		new_content = request.form['new_content']
		comment.content = new_content	
	
		db.session.commit()
	
		return redirect(request.referrer)
	
	else:
		return render_template('update_comment.html', comment=comment)	

@app.route('/delete_group/<int:id>')
def delete_group(id):
    group_to_delete = Group.query.get(int(id))

    try:
        db.session.delete(group_to_delete)
        db.session.commit()
        return redirect(request.referrer)
    except:
        return "There was a problem deleting this group!"
        
@app.route('/delete_post/<int:id>')
def delete_post(id):
    post_to_delete = Post.query.get(int(id))

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(request.referrer)
    except:
        return "There was a problem deleting this post!"     
        
@app.route('/delete_comment/<int:id>')
def delete_comment(id):
    comment_to_delete = Comment.query.get(int(id))

    try:
        db.session.delete(comment_to_delete)
        db.session.commit()
        return redirect(request.referrer)
    except:
        return "There was a problem deleting this comment!"           
