from flask import Flask, render_template
from flask import request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from functools import wraps

from flask_security import Security
from flask_security import SQLAlchemyUserDatastore
from flask_security import RoleMixin, UserMixin
from flask_security import current_user, login_required
from flask_security.forms import RegisterForm, LoginForm

from wtforms import StringField, TextAreaField, SelectField, DateField
from wtforms.validators import InputRequired
from flask_wtf import FlaskForm 
from datetime import datetime

import os
import random
import string
from hashlib import sha512
import base64
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"

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
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# For more useful resources: https://flask-security-too.readthedocs.io/_/downloads/en/stable/pdf/


db = SQLAlchemy(app)
migrate = Migrate(app, db)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

groups_users = db.Table('groups_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer(), db.ForeignKey('group.id')))

events_to_posts = db.Table('events_to_posts',
	db.Column('event_id', db.Integer(), db.ForeignKey('event.id')),
	db.Column('post_id', db.Integer(), db.ForeignKey('post.id')))

guests_to_events = db.Table('guests_to_events',
	db.Column('event_id', db.Integer(), db.ForeignKey('event.id')),
	db.Column('user_id', db.Integer(), db.ForeignKey('user.id')))

polls_users = db.Table('polls_users', 
	db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
	db.Column('poll_id', db.Integer(), db.ForeignKey('poll.id')))

apply_admins = db.Table('apply_admins',
	db.Column('apply_id', db.Integer(), db.ForeignKey('apply.id')),
	db.Column('admin_id', db.Integer(), db.ForeignKey('admin.id')))

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
	gender = db.Column(db.String(30), unique=False, nullable=False)
	status = db.Column(db.String(30), unique=False, nullable=False)
	active = db.Column(db.Boolean())
	confirmed_at = db.Column(db.DateTime(), default = datetime.now())
	profile_photo = db.Column(db.String(300), unique = True, nullable = True)
    
	roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
	groups = db.relationship('Group', secondary=groups_users, backref=db.backref('users', lazy='dynamic'))
	posts = db.relationship('Post', backref='post', lazy='dynamic')
	comments = db.relationship('Comment', backref='comment', lazy='dynamic')
	polls = db.relationship('Poll', secondary=polls_users, backref=db.backref('polls', lazy='dynamic'))

class Admin(db.Model):
	__tablename__ = 'admin'
	id = db.Column(db.Integer(), primary_key=True)
	user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	group_id = db.Column(db.Integer(), db.ForeignKey('group.id'))	

class Group(db.Model):
	__tablename__ = 'group'
	id = db.Column(db.Integer(), primary_key = True)
	name = db.Column(db.String(300))
	description = db.Column(db.String(3000))
	date_created = db.Column(db.DateTime())
    
	admin_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	posts = db.relationship('Post', backref='group', lazy='dynamic')
   	
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer(), primary_key = True)
    content = db.Column(db.String(300), unique = False, nullable = False)
    date_created = db.Column(db.DateTime())
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    file_name = db.Column(db.String(300), unique = False, nullable = True)
    actual_filename = db.Column(db.String(300), unique = False, nullable = True)
    access = db.Column(db.String(10), unique=False, nullable=False)
    
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    #event_id = db.Column(db.Integer(), db.ForeignKey('event.id'), nullable=True)
    group_id = db.Column(db.Integer(), db.ForeignKey('group.id'), nullable=True)

class Comment(db.Model):
	__tablename__ = 'comment'
	id = db.Column(db.Integer(), primary_key = True)
	content = db.Column(db.String(300), unique = False, nullable = False)
	date_created = db.Column(db.DateTime())
	file_name = db.Column(db.String(300), unique = False, nullable = True)    
	actual_filename = db.Column(db.String(300), unique = False, nullable = True)
    
	user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))

class Event(db.Model):
	__tablename__ = 'event'

	id = db.Column(db.Integer(), primary_key = True)    
	name = db.Column(db.String(30), unique = False, nullable = False)
	date_happening = db.Column(db.DateTime(), default = datetime.now())
	date_event = db.Column(db.DateTime(), default = datetime.now())
	max_guests = db.Column(db.Integer(), default=0)
	current_guests = db.Column(db.Integer(), default=1)
	access = db.Column(db.String(10), unique=False, nullable=False)
   	
	user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	group_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=True)
	posts = db.relationship('Post', secondary=events_to_posts, backref = db.backref('events', lazy = 'dynamic'))    
	guests = db.relationship('User', secondary=guests_to_events, backref=db.backref('event', lazy= 'dynamic'))

class Poll(db.Model):
	__tablename__ = 'poll'

	id = db.Column(db.Integer(), primary_key = True)    
	date_created = db.Column(db.DateTime(), default=datetime.now())
	current_option = db.Column(db.Integer(), nullable=False, default=0)
    
	user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	group_id = db.Column(db.Integer(), db.ForeignKey('group.id'), nullable=True)    	

class Question(db.Model):
	__tablename__ = 'question'

	id = db.Column(db.Integer(), primary_key = True)    
	content = db.Column(db.String(300), unique = False, nullable = False, default="Question")	
    
	poll_id = db.Column(db.Integer(), db.ForeignKey('poll.id'), nullable=False)

class Option(db.Model):
	__tablename__ = 'option'
	
	id = db.Column(db.Integer(), primary_key = True)    
	content = db.Column(db.String(300), unique = False, nullable = False, default="Option")	
	count = db.Column(db.Integer(), nullable=False, default = 0)
    
	question_id = db.Column(db.Integer(), db.ForeignKey('question.id'), nullable=False)

class Apply(db.Model):
	__tablename__ = 'apply'
	id = db.Column(db.Integer(), primary_key = True)	
	content = db.Column(db.String(1000), unique = False, nullable = False)
	username = db.Column(db.String(300), unique=True, nullable=False)
	group_name = db.Column(db.String(300))  
    
	user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	admins = db.relationship('Admin', secondary=apply_admins, backref=db.backref('applications', lazy='dynamic'))
	group_id = db.Column(db.Integer(), db.ForeignKey('group.id'))   

class GroupInvite(db.Model):
	__tablename__ = 'group_invite'
	id = db.Column(db.Integer(), primary_key=True)
	
	sender_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	receiver_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	group_id = db.Column(db.Integer(), db.ForeignKey('group.id'))

class EventInvite(db.Model):
	__tablename__ = 'event_invite'
	id = db.Column(db.Integer(), primary_key=True)
	
	sender_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	receiver_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))

class PostPicture(db.Model):
    __tablename__ = 'post_photo'

    id = db.Column(db.Integer(), primary_key = True)
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'), unique = True)
    

class CommentPicture(db.Model):
    __tablename__ = 'comment_photo'

    id = db.Column(db.Integer(), primary_key = True)
    comment_id = db.Column(db.Integer(), db.ForeignKey('comment.id'), unique = True)

class New_Group(FlaskForm):
    name = StringField('Title')
    description = StringField('Description')

class New_Post(FlaskForm):
    content = TextAreaField('Content')

class New_Comment(FlaskForm):
    content = TextAreaField('Content')

class New_Event(FlaskForm):
	name = StringField('Name')
	date = DateField('Date', format='%Y-%m-%d')
	access = SelectField('Access', choices=[('public', 'Public'), ('private', 'Private')], coerce=str)
	max_guests = SelectField('Participants', choices=[('10', '10'), ('25', '25'), ('50', '50'), ('100', '100')], coerce=int)

class ExtendRegisterForm(RegisterForm):
    name = StringField('Name')
    username = StringField('Username')
    
    age = SelectField('Age', choices = [('13', '13'), ('14', '14'), ('15', '15'),
                                        ('16', '16'), ('17', '17'), ('18', '18'),
                                        ('19', '19'), ('20', '20'), ('21', '21'),
                                        ('22', '22'), ('23', '23'), ('24', '24'),
                                        ('25', '25'), ('26', '26'), ('27', '27'),
                                        ('28', '28'), ('29', '29'), ('30', '30'),
                                        ('31', '31'), ('32', '32'), ('33', '33')])
    gender = SelectField("Sex", choices=[('Male', 'Male'), ('Female', 'Female')])
    status = SelectField("Status", choices=[('School Student', 'School Student'), 
                                            ('High School Student', 'High School Student'),
                                            ('College Student', 'College Student'),
                                            ('Employed Graduated Student', 'Employed Graduated Student'), 
                                            ('Unemployed Graduated Student', 'Unemployed Graduated Student')])

class ExtendLoginForm(LoginForm):
    email = StringField('Username', [InputRequired()])


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_form=ExtendRegisterForm, login_form=ExtendLoginForm)

def require_login(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if not current_user.is_authenticated:
			return redirect('/login')
		return func(*args, **kwargs)
	return wrapper

def random_string(length):
	return ''.join(random.choice(string.ascii_letters) for x in range(length))

@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		
		file = request.files['register_file']

		if file and file.filename != '':
			new_filename = random_string(100)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html', current_user=current_user)

@app.route('/all_groups', methods=['GET', 'POST'])
@require_login
def all_groups():

	form = New_Group()

	if request.method == 'POST': 
		if form.validate_on_submit():
			new_group = Group(name=form.name.data, description=form.description.data, date_created=datetime.now(), admin_id=current_user.id)
			db.session.add(new_group)
			db.session.commit()
			new_admin = Admin(user_id = current_user.id, group_id=new_group.id)
			db.session.add(new_admin)
			new_group.users.append(current_user)
			db.session.commit()
        	
		else:
			keyword = request.form['keyword']
		
			group_size = 5
			group_names = [group.name for group in Group.query.all()]
	
			if len(group_names) < 5:
				group_size = len(group_names)
				
			groups = []
			posts = []
			events = []
			users = User.query.all()
				
			if Group.query.all():
				needed_groups = process.extract(keyword, group_names, limit=group_size)	
		
				for single in needed_groups:
					groups.append(Group.query.filter_by(name=single[0]).first())		
			
				
			return render_template('all_groups.html', form=form, groups=groups, current_user=current_user)

	groups = Group.query.all()
	inside_groups = []
	
	for group in groups:
		if current_user in group.users:
			inside_groups.append(group)
	
	return render_template('all_groups.html', form=form, groups=inside_groups, current_user=current_user)

@app.route('/group/<group_id>/calendar', methods=['GET', 'POST'])
@require_login
def group_calendar(group_id):

	form = New_Event()
	if request.method == 'POST' and form.validate_on_submit():
		
		new_event = Event(name=form.name.data, date_happening=form.date.data, user_id=current_user.id, group_id=group_id, access=form.access.data, max_guests=form.max_guests.data)
		db.session.add(new_event)
		db.session.commit()

		return redirect(request.referrer)

	else:
		events = Event.query.filter_by(group_id=group_id)
		return render_template('group_calendar.html', events=events, form=form, groups=[])

@app.route('/group/<group_id>', methods=['GET', 'POST'])
@require_login
def group(group_id):
	form = New_Post()
	group = Group.query.get(int(group_id))

	if request.method == 'POST':
	
		if "fuzzy" in request.form:
			keyword = request.form['keyword']
			posts_contents = [post.content for post in group.posts]
			max_elements = 5
			posts = []
			
			if len(posts_contents) < max_elements:
				max_elements = len(posts_contents)
			
			users = group.users
						
			if group.posts:
				needed = process.extract(keyword, posts_contents, limit=max_elements)
				
				for single in needed:
					posts.append(Post.query.filter_by(content=single[0]).first())
			
			return render_template('group.html', group=group, form=form, posts=posts, users=users, current_user=current_user)
	
		elif "post" in request.form:
			#try:
        
				file = request.files['post_file']

				if file and file.filename != '':
					new_filename = random_string(100)
					file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
					new_post = Post(user_id=current_user.id, content = request.form['post_content'], date_created=datetime.now(), group_id=group_id, file_name=new_filename, actual_filename = file.filename, access=request.form['access'])
        		
				else:
					new_post = Post(user_id=current_user.id, content = request.form['post_content'], date_created=datetime.now(), group_id=group_id, access=request.form['access'])
        			
				group.posts.append(new_post)
				db.session.commit()
			#except:
				#return "There was a problem adding a new post on this topic!"

	posts = Post.query.filter_by(group_id=group_id).all()
	users = group.users
	admins = Admin.query.filter_by(group_id=group.id).all()
	admin_users = []
	
	for user in users:
		for admin in admins:
			if user.id == admin.user_id:
				admin_users.append(user)
							
				
	return render_template('group.html', group=group, form=form, posts=posts, users=users, current_user=current_user, admins=admin_users)

@app.route('/post/<post_id>', methods=['GET', 'POST'])
@require_login
def post(post_id):

	post = Post.query.get(int(post_id))
	comment_form = New_Comment()
    
	if request.method == 'POST':  
      
		if "comment" in request.form:
			#try:
        	
				file = request.files['comment_file']

				if file and file.filename != '':
					new_filename = random_string(100)
					file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
					new_comment = Comment(content=request.form["comment_content"], date_created=datetime.now(), user_id=current_user.id, post_id=post.id, file_name = new_filename, actual_filename = file.filename)
        			
				else:
					new_comment = Comment(content=request.form["comment_content"], date_created=datetime.now(), user_id=current_user.id, post_id=post.id)
        			
				post.comments.append(new_comment)
				db.session.commit()
				         	
				return request.referrer
			#except:
				#return "There was a problem adding a new comment on this post!"			


		else:
			event_id = request.form['event']
			event = Event.query.get(int(event_id))
			post.events.append(event)
			event.posts.append(post)
			db.session.commit()
			return redirect('post/<int:id>')
			

	else:
		comments = Comment.query.filter_by(post_id=post_id).all()
		linked_to = post.events
		all_events = Event.query.all()
		unlinked = []

		for event in all_events:
			if not event in linked_to:
				unlinked.append(event)
		return render_template('post.html', post=post, form=comment_form, linked_to=linked_to, unlinked=unlinked, current_user=current_user, comments=comments)


@app.route('/apply_for_group/<group_id>', methods = ['GET', 'POST'])
@require_login
def apply_for_group(group_id):
	group = Group.query.get(int(group_id))
	
	if request.method == 'POST':
		
		admin = User.query.filter_by(id=group.admin_id).first()
		admins = Admin.query.filter_by(group_id=group.id).all()
		admin_users = []
		users = User.query.all()
				
		appliance = Apply(content=request.form['appliance_content'], user_id=current_user.id, admins=admins, group_id=group.id, username = current_user.username, group_name = group.name)
		db.session.add(appliance)
		db.session.commit()
	
		return redirect(request.referrer)
	
	else:
		return render_template('apply_for_group.html', current_user=current_user, group=group)
		
@app.route('/group/<group_id>/join_requests')
def join_requests(group_id):		
	
	applications = Apply.query.all()
	needed = []

	for appply in applications:
		for admin in appply.admins:
			if current_user.id == admin.user_id:
				needed.append(appply)
				
	return render_template('join_requests.html', applications=needed)	

@app.route('/apply/<int:apply_id>', methods = ['POST', 'GET'])
@require_login
def apply(apply_id):
	
	appliance = Apply.query.filter_by(id = apply_id).first()
	content = appliance.content
	user = User.query.filter_by(id=appliance.user_id).first()	
	admin = Admin.query.filter_by(user_id=current_user.id, group_id=appliance.group_id).first()
	
	if request.method == 'POST':
		
		answer = request.form['answer']
		group = Group.query.filter_by(id=appliance.id).first()
	
		if answer == "Yes" and group not in user.groups:
			user.groups.append(group)
	
		db.session.delete(appliance)
		db.session.commit()
	
		return redirect('/all_groups')
	
	else:
		return render_template('apply.html', content=content, user=user, apply_id=apply_id)

@app.route('/update_group/<group_id>', methods = ['POST', 'GET'])
@require_login
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
@require_login
def update_post(post_id):
    post_to_delete = Post.query.get(int(post_id))	
		
    if post_to_delete.user_id != current_user.id:
        return redirect('/all_groups')	
		
    if request.method == 'POST':		
		
        new_content = request.form['new_content']
        post.content = new_content	
	
        db.session.commit()
	
        return redirect(request.referrer)
	
    else:
	
        return render_template('update_post.html', post=post)	

@app.route('/update_comment/<comment_id>', methods = ['POST', 'GET'])
@require_login
def update_comment(comment_id):
	comment = Comment.query.get(int(comment_id))
		
	if comment_to_delete.user_id != current_user.id:
		return redirect('/all_groups')	
		
	if request.method == 'POST':	
		
		new_content = request.form['new_content']
		comment.content = new_content	
	
		db.session.commit()
	
		return redirect(request.referrer)
	
	else:
		return render_template('update_comment.html', comment=comment)	

@app.route('/delete_group/<int:id>')
@require_login
def delete_group(id):
	group_to_delete = Group.query.get(int(id))

	try:
		db.session.delete(group_to_delete)
		db.session.commit()
		return redirect(request.referrer)
	except:
		return "There was a problem deleting this group!"
        
@app.route('/delete_post/<int:id>', methods = ['GET'])
@require_login
def delete_post(id):
	post_to_delete = Post.query.get(int(id))

	events = post_to_delete.events
		
	for event in events:
		event.posts.remove(post_to_delete)
	try:	
		db.session.delete(post_to_delete)
		db.session.commit()
		return redirect(request.referrer)
	except:
		return "There was a problem deleting this post!"     
        
@app.route('/delete_comment/<int:id>')
@require_login
def delete_comment(id):
    comment_to_delete = Comment.query.get(int(id))
	
    try:
        db.session.delete(comment_to_delete)
        db.session.commit()
        return redirect(request.referrer)
    except:
        return "There was a problem deleting this comment!"       
        
@app.route('/personal_calendar', methods = ['GET', 'POST'])
@require_login
def personal_calendar():

	form = New_Event()
	if request.method == 'POST':
		
		if form.validate_on_submit():
		
			new_event = Event(name=form.name.data, date_happening=form.date.data, user_id=current_user.id, access=form.access.data, max_guests=form.max_guests.data)
			db.session.add(new_event)
			db.session.commit()
			
			return redirect('/personal_calendar')

		elif "filter" in request.form:
			values = request.form.getlist('options')
			events_to_show = []

			for value in values:
				if value == 'personal':
					personal = Event.query.filter_by(user_id=current_user.id).all()
					
					
					for event in personal:
						events_to_show.append(event)
			
				elif value == 'invited to':
					for event in current_user.event:
						events_to_show.append(event)
			
				else:
					group = Group.query.filter_by(name=value).first()
					events = Event.query.filter_by(group_id=group.id).all()
					
					for event in events:
						events_to_show.append(event)	
			
			return render_template('calendar_view.html', events=events_to_show, form=form, groups=current_user.groups)

	else:
		events = Event.query.all()
		groups = Group.query.all()
		events_in = []
		groups_in = [group for group in groups if group in current_user.groups]
		
		for event in events:
			if current_user in event.guests or current_user.id == event.user_id:
				events_in.append(event)
				
		for group in groups_in:
			for event in events:
				if event.group_id == group.id:
					events_in.append(event)
		
		group = current_user.groups
											
		return render_template('calendar_view.html', events=events_in, form=form, groups=groups)
		
@app.route('/events/<int:id>', methods = ['GET', 'POST'])
@require_login
def event(id):

	event = Event.query.get(int(id))
	
	if request.method == "POST":
	
		if "post" in request.form:
			#try:
        
			file = request.files['post_file']

			if file and file.filename != '':
				new_filename = random_string(100)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
				new_post = Post(user_id=current_user.id, content = request.form['post_content'], date_created=datetime.now(), file_name=new_filename, actual_filename = file.filename, access=request.form['access'])
				db.session.add(new_post)
				event.posts.append(new_post)
				db.session.commit()			
				return redirect(request.referrer)
        		
			else:
				new_post = Post(user_id=current_user.id, content = request.form['post_content'], date_created=datetime.now(), access=request.form['access'])
				db.session.add(new_post)
				event.posts.append(new_post)
				db.session.commit()			
				return redirect(request.referrer)	
		
		
		elif "assign" in request.form:
			event.guests.append(current_user)
			event.current_guests += 1
			db.session.commit()
		
			return redirect(request.referrer)
		
		else:
		
			post_id = request.form['event']
			post = Post.query.get(int(post_id))
			post.events.append(event)
			event.posts.append(post)
			db.session.commit()
			
			return redirect(request.referrer)

	else:
		linked_posts = event.posts
		all_posts = Post.query.all()
		unlinked_posts = []
		
		for post in all_posts:
			if post not in linked_posts:
				unlinked_posts.append(post)
				
		return render_template('event.html', event=event, linked_posts=linked_posts, unlinked_posts=unlinked_posts, user=current_user)

@app.route('/update_event/<int:id>', methods = ['GET', 'POST'])
@require_login
def update_event(id):
	event = Event.query.get(int(id))
    
	if event.user_id != current_user.id:
		return redirect('/events/<int:id>')
   
	if request.method == 'POST':	
		
		new_name = request.form['name']
		new_date = request.form['date']
		event.name = new_name	
		event.date_happening = new_date
		
		db.session.commit()
	
		return redirect('/events/<ind:id>')
	
	else:
		return render_template('update_event.html', event=event)	    
        
@app.route('/delete_event/<int:id>')
@require_login
def delete_event(id):
	event = Event.query.get(int(id))
	
	if event.user_id != current_user.id:
		return redirect('/event/<int:id>')		

	try:
		posts = event.posts
    	
		for post in posts:
			post.events.remove(event)
    		
		db.session.delete(event)	
		db.session.commit()
        
		return redirect('/calendar_view')
    
	except:
		return "There was a problem deleting this event!"

@app.route('/group/<int:group_id>/create_poll', methods = ['GET', 'POST'])
@require_login		
def create_poll(group_id):
	
	if request.method == "POST":
		
		poll = Poll.query.filter_by(id=request.form['poll_id']).first()
		question = Question.query.filter_by(poll_id=poll.id).first()	
	
		if request.form['question'] is not question.content:
			question.content = request.form['question']
				
		options=Option.query.filter_by(question_id=question.id)
			
		for option in options:
			option.content = request.form[str(option.id)]
	
		if "opt" in request.form: #adding another option to the question
			
			option = Option(question_id=question.id, content=request.form['opt'])
			
			db.session.add(option)
			db.session.commit()
			
			return render_template('create_poll.html', poll=poll, question=question, options=Option.query.filter_by(question_id=question.id))	
			
		else:#submiting all final changes to the base				 	
			db.session.commit()
			
			return redirect('/group/<int:group_id>/polls')
	
	else:
	
		#generating custom question with 2 possible options. more options could be added
		poll = Poll(user_id=current_user.id, group_id=group_id)
		db.session.add(poll)
		db.session.commit()
		
		question = Question(poll_id=poll.id)
		db.session.add(question)
		db.session.commit()
		
		option1 = Option(question_id=question.id)
		option2 = Option(question_id=question.id)
		
		db.session.add(option1)		
		db.session.add(option2)		

		db.session.commit()
		
		return render_template('create_poll.html', poll=poll, question=question, options=Option.query.filter_by(question_id=question.id))	


@app.route('/group/<group_id>/polls', methods = ['GET', 'POST'])
@require_login				
def polls(group_id):

	if request.method == 'POST':
	
		poll = Poll.query.filter_by(id=request.form['poll_id']).first()
		question = Question.query.filter_by(poll_id=poll.id).first()
	
		if "poll-first" in request.form:	
			current_user.polls.append(poll)
			option = Option.query.filter_by(id=request.form['option_id']).first()
			poll.current_option = option.id;
			option.count += 1
		
		elif "poll-change" in request.form:
			curr_option = Option.query.filter_by(id=poll.current_option).first()
			curr_option.count -= 1
		
			new_option = Option.query.filter_by(id=request.form['option_id']).first()
			new_option.count += 1
			poll.current_option = new_option.id
		
		db.session.commit() 
				
		return redirect(request.referrer)			
	
	else:
	
		polls = Poll.query.filter_by(group_id=group_id)
		voted = []
		unvoted = []
	
		for poll in polls:
			
			package = {}	
			package['poll'] = poll
			question = Question.query.filter_by(poll_id=poll.id).first()
			package['question'] = question
			options = Option.query.filter_by(question_id=question.id)
			package['options'] = options
			
			if poll in current_user.polls:
				voted.append(package)
			
			else:
				unvoted.append(package)
		
		return render_template('polls.html', voted=voted, unvoted=unvoted)
		
@app.route('/group/<group_id>/members', methods=['GET', 'POST'])
@require_login
def members(group_id):
	
	group = Group.query.get(int(group_id))
	if request.method == "POST":						
		
		if "fuzzy" in request.form:
			keyword = request.form['keyword']
			users_names = [user.name for user in group.users]
			max_elements = 5
			users = []
			
			if len(users_names) < max_elements:
				max_elements = len(users_names)
			
			if group.users:
				needed = process.extract(keyword, users_names, limit=max_elements)
				
				for single in needed:
					users.append(User.query.filter_by(name=single[0]).first())
			
			admins = Admin.query.filter_by(group_id=group.id).all()
			admin_users = []
	
			for user in users:
				for admin in admins:
					if admin.user_id == user.id:
						admin_users.append(user)
					
			return render_template('members.html', members=users, admins=admin_users, current_user=current_user, group=group)				
			
		user = User.query.filter_by(id=request.form.get('member_id')).first()
		
		if "kick" in request.form:
			group.users.remove(user)
			db.session.commit()
			return redirect(request.referrer)
			
		elif "promote" in request.form:
			
			new_admin = Admin(user_id = user.id, group_id = group.id)
			db.session.add(new_admin)
			db.session.commit()
			return redirect(request.referrer)	
	
	
	else:
		members = group.users
		admins = Admin.query.filter_by(group_id=group.id).all()
		admin_users = []
	
		for member in members:
			for admin in admins:
				if admin.user_id == member.id:
					admin_users.append(member)
					
		return render_template('members.html', members=members, admins=admin_users, current_user=current_user, group=group)	

@app.route('/user/<user_id>', methods = ['GET'])
@require_login		
def inspect_profile(user_id):

	user = User.query.get(int(user_id))		
	return render_template('check_user_profile.html', user=user)
	
	
@app.route('/search', methods = ['GET', 'POST'])
@require_login
def search():

	if request.method == "POST":
		if "fuzzy" in request.form:
				
			keyword = request.form['keyword']
		
			group_size = 5
			post_size = 5
			event_size = 5
			user_size = 5

			group_names = [group.name for group in Group.query.all()]
			post_contents = [post.content for post in Post.query.filter_by(access="public").all()]
			event_names = [event.name for event in Event.query.filter_by(access="public").all()]
			user_names = [user.name for user in User.query.all()]
	
	
			if len(group_names) < 5:
				group_size = len(group_names)
				
			if len(post_contents) < 5:
				post_size = len(post_contents)
				
			if len(event_names) < 5:
				event_size = len(event_names)
				
			if len(user_names) < 5:
				user_size = len(user_names)		
	
	
			groups = []
			posts = []
			events = []
			users = []
				
			if Group.query.all():
				needed_groups = process.extract(keyword, group_names, limit=group_size)	
		
				for single in needed_groups:
					groups.append(Group.query.filter_by(name=single[0]).first())		
			
			if User.query.all():
				needed_users = process.extract(keyword, user_names, limit=user_size)	
		
				for single in needed_users:
					users.append(User.query.filter_by(name=single[0]).first())
			
			if Post.query.filter_by(access="public").all():
				needed_posts = process.extract(keyword, post_contents, limit=post_size)	
		
				for single in needed_posts:
					posts.append(Post.query.filter_by(content=single[0]).first())
			
			if Event.query.filter_by(access="public").all():
				needed_events = process.extract(keyword, event_names, limit=event_size)	
		
				for single in needed_events:
					events.append(Event.query.filter_by(name=single[0]).first())			
		
		return render_template('search.html', current_user=current_user, groups=groups, posts=posts, events=events, users=users)
		
	else:
	
		return render_template('search.html', current_user=current_user, groups=[], posts=[], events=[], users=[])	
		
		
@app.route('/group/<group_id>/add_people', methods = ['GET', 'POST'])
@require_login
def add_people(group_id):

	group = Group.query.get(int(group_id))

	if request.method == 'POST':
	
		if "fuzzy" in request.form:
				
			keyword = request.form['keyword']
		
			user_size = 5
			user_names = [user.name for user in User.query.all()]
	
			if len(user_names) < 5:
				user_size = len(user_names)		
			
			users = User.query.all()
			users_to_show = []
			
			if users:
				needed_users = process.extract(keyword, user_names, limit=user_size)	
		
				for single in needed_users:
					users_to_show.append(User.query.filter_by(name=single[0]).first())

			admins = group.admins
			user_admins = []
					
			for user in users:
				for admin in admins:
					if user.id == admin.user_id:
						user_admins.append(user)
	
			return render_template('add_people.html', current_user=current_user, admins=admins, users=users_to_show, group=group)
		
		elif "invite" in request.form: 
	
			user = User.query.filter_by(id=request.form.get('user_id')).first()
			new_group_invite = GroupInvite(sender_id=current_user.id, receiver_id=user.id, group_id=group.id)
			db.session.add(new_group_invite)
			db.session.commit()
	
			return redirect(request.referrer)
	
	else:	
		
		admins = Admin.query.filter_by(group_id=group.id).all()
		users = User.query.all()
		user_admins = []
		group_users = group.users
		users_to_show = []
		
		for user in users:
			if user not in group_users:
				users_to_show.append(user)				
					
		for user in users:
			for admin in admins:
				if user.id == admin.user_id:
					user_admins.append(user)
	
		return render_template('add_people.html', current_user=current_user, users=users_to_show, admins=user_admins, group=group)
	
		
@app.route('/invitations', methods = ['GET', 'POST'])
@require_login
def invitations():

	if request.method == "POST":
		
		if "confirm" in request.form:
			event_invite = EventInvite.query.filter_by(id=request.form['confirm_id']).first()
			event = Event.query.filter_by(id=event_invite.event_id).first()
			event.guests.append(current_user)
			event.current_guests += 1 
			to_be_cleared = EventInvite.query.filter_by(event_id=event.id, receiver_id=current_user.id).all()
			for invite in to_be_cleared:
				db.session.delete(invite)
			
			db.session.commit()	
			return redirect(request.referrer)

		elif "discard" in request.form:
			event_invite = EventInvite.query.filter_by(id=request.form['discard_id']).first()
			db.session.delete(event_invite)
			db.session.commit()
	
			return redirect(request.referrer)
			
		elif "accept" in request.form:
			group_invite = GroupInvite.query.filter_by(id=request.form['invite_id']).first()
			group = Group.query.filter_by(id=group_invite.group_id).first()
			group.users.append(current_user)
			to_be_cleared = GroupInvite.query.filter_by(group_id=group.id, receiver_id=current_user.id).all()
			for invite in to_be_cleared:
				db.session.delete(invite)
			
			db.session.commit()	
			return redirect(request.referrer)
	
		else:
			group_invite = GroupInvite.query.filter_by(id=request.form['decline_id']).first()
			db.session.delete(group_invite)
			db.session.commit()
	
			return redirect(request.referrer)
	else:
		invite_packs = []
		invitations = GroupInvite.query.filter_by(receiver_id=current_user.id).all()
		
		for invite in invitations:
			pack = {}
			sender = User.query.filter_by(id=invite.sender_id).first()
			group = Group.query.filter_by(id=invite.group_id).first()
			pack["invite"] = invite
			pack["sender"] = sender
			pack["group"] = group
			invite_packs.append(pack)
		
		event_packs = []
		event_invitations = EventInvite.query.filter_by(receiver_id=current_user.id).all()
		
		for invite in event_invitations:
			pack = {}
			sender = User.query.filter_by(id=invite.sender_id).first()
			event = Event.query.filter_by(id=invite.event_id).first()
			pack["invite"] = invite
			pack["sender"] = sender
			pack["event"] = event
			event_packs.append(pack)
			
		return render_template('invitations.html', current_user=current_user, invites=invite_packs, event_invites=event_packs)
		
@app.route('/invite_to_event/<event_id>', methods = ['GET', 'POST'])
@require_login
def invite_to_event(event_id):

	event = Event.query.get(int(event_id))

	if request.method == "POST":

		if "fuzzy" in request.form:
				
				keyword = request.form['keyword']
		
				user_size = 5
				user_names = [user.name for user in User.query.all()]
	
				if len(user_names) < 5:
					user_size = len(user_names)		
			
				users = User.query.all()
				users_to_show = []
			
				if users:
					needed_users = process.extract(keyword, user_names, limit=user_size)	
			
					for single in needed_users:
						users_to_show.append(User.query.filter_by(name=single[0]).first())

				return render_template('invite_to_events.html', current_user=current_user, users=users_to_show, event=event)
		
		elif "invite" in request.form: 
		
			user = User.query.filter_by(id=request.form.get('user_id')).first()
			new_event_invite = EventInvite(sender_id=current_user.id, receiver_id=user.id, event_id=event.id)
			db.session.add(new_event_invite)
			db.session.commit()
	
			return redirect(request.referrer)
	
	else:	
		
		users = User.query.all()
		guests = event.guests
		user_guests = []
	
		for user in users:
			if guests:
				for guest in guests:
					if guest.id != user.id:
						user_guests.append(user)
			
			else:
				user_guests.append(user)
		return render_template('invite_to_events.html', current_user=current_user, users=user_guests, event=event)				
						
