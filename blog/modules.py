from datetime import datetime
from blog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id): 
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False)
	email = db.Column(db.String(120), nullable=False, unique=True)
	usertype = db.Column(db.String(20), nullable=False, default='User')
	password = db.Column(db.String(60), nullable=False)

class Subject(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False, unique=True)
	purpose = db.Column(db.Text, nullable=False)
	status = db.Column(db.String(20), default='UnApproved')
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	authorEmail = db.Column(db.String(20), nullable=False)
	articles = db.relationship('Article', backref='subject', lazy='dynamic')


class Article(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(20), nullable=False)
	body = db.Column(db.Text, nullable=False)
	articlefile = db.Column(db.String(30), nullable=True)
	authorEmail = db.Column(db.String(20), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
	comments = db.relationship('Comment', backref='article', lazy='dynamic')
	likes = db.relationship('LikeArticle', backref='article', lazy='dynamic')
	dislikes = db.relationship('DisLikeArticle', backref='article', lazy='dynamic')
	visitors = db.relationship('Visitor', backref='article', lazy='dynamic')

class Visitor(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	visitor_ip = db.Column(db.String(10), nullable=False)
	article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)

class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.Text, nullable=False)
	authorEmail = db.Column(db.String(20), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)


class LikeArticle(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
	author_ip = db.Column(db.String(100), nullable=False)

class DisLikeArticle(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
	author_ip = db.Column(db.String(100), nullable=False)