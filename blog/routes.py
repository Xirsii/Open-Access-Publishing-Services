import os
from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from blog import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import secrets
from blog.modules import Article, Comment, User, Subject, DisLikeArticle, LikeArticle, Visitor
from blog.forms import (ArticleForm, CommentForm, LoginForm,
RegistrationForm, RegistrationForm, LoginForm, SubjectForm, EditSubjectForm)
from sqlalchemy import or_, and_
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = basedir + '/static/articlefiles'
app.config['UPLOAD_FOLDER'] = os.path.join(basedir+'/static/articlefiles')

# ===============================================================================
# 			download article file "root"
# ===============================================================================
@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename, as_attachment=True)

# ===============================================================================
# 			search "root"
# ===============================================================================
@app.route('/Search', methods=['GET', 'POST'])
def search():
	content = request.args.get('content')
	articles = db.session.query(Article).filter(Article.body.contains(content)).all()

	comments = db.session.query(Comment).filter(Comment.content.contains(content)).all()

	subjects = db.session.query(Subject).filter(Subject.name.contains(content)).all()

	return render_template('searchresult.html', articles=articles, comments=comments,
	subjects=subjects, content=content, request=request)

# ===============================================================================
# 							authenticated user dashboard "root"
# ===============================================================================
@app.route('/Dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	# this page can access only authicated users
	if current_user.usertype == 'User':
		my_subjects = Subject.query.filter(Subject.authorEmail == current_user.email).all()
		my_articles = Article.query.filter(Article.authorEmail == current_user.email).all()
		if my_subjects or my_articles:
			return render_template('dashboard.html', my_subjects=my_subjects, my_articles=my_articles)
		else:
			flash('You have no subjects so far', 'info')
			return redirect(url_for('Subjects'))
	else:# if user tries to access this page from url
		flash('Access Dinied', 'danger')
		return redirect(url_for('Subjects'))

# ===============================================================================
# 				like article "root"
# ===============================================================================
@app.route('/like', methods=['POST'])
def like():
	art_id = request.form['article_id']
	ip_add = request.remote_addr
	already_liked = LikeArticle.query.filter(and_(LikeArticle.article_id == art_id,
	LikeArticle.author_ip == ip_add)).first()
	already_disliked = DisLikeArticle.query.filter(and_(DisLikeArticle.article_id == art_id,
	DisLikeArticle.author_ip == ip_add)).first()
	if already_liked and not already_disliked:
		# if current_user already like this article and click again like button we will undo his/her previous like
		db.session.delete(already_liked)
		db.session.commit()
		likes = LikeArticle.query.filter(LikeArticle.article_id == art_id).count()
		dislikes = DisLikeArticle.query.filter(DisLikeArticle.article_id == art_id).count()
		data = {
			"likes": likes,
			"dislikes": dislikes
		}
		return jsonify({'data' : data})
	elif not already_liked and already_disliked:
		# if current_user already dislike this article and click like button we will delete his/her previous dislike 
		db.session.delete(already_disliked)
		db.session.commit()
		likes = LikeArticle.query.filter(LikeArticle.article_id == art_id).count()
		dislikes = DisLikeArticle.query.filter(DisLikeArticle.article_id == art_id).count()
		data = {
			"likes": likes,
			"dislikes": dislikes
		}
		return jsonify({'data' : data})
		return 'we have cancel your previous dislike'
	else:
		# if current_user didn't like and dislike this article yet we will record his/her like
		like = LikeArticle(article_id=art_id, author_ip=ip_add)
		db.session.add(like)
		db.session.commit()
		likes = LikeArticle.query.filter(LikeArticle.article_id == art_id).count()
		dislikes = DisLikeArticle.query.filter(DisLikeArticle.article_id == art_id).count()
		data = {
			"likes": likes,
			"dislikes": dislikes
		}
		return jsonify({'data' : data})

# ===============================================================================
# 			dislike article "root"
# ===============================================================================
@app.route('/dislike', methods=['POST']) 
def dislike():
	art_id = request.form['article_id']
	ip_add = request.remote_addr
	already_liked = LikeArticle.query.filter(and_(LikeArticle.article_id == art_id,
	LikeArticle.author_ip == ip_add)).first()
	already_disliked = DisLikeArticle.query.filter(and_(DisLikeArticle.article_id == art_id,
	DisLikeArticle.author_ip == ip_add)).first()
	if already_disliked and not already_liked:
		# if current_user already dislike this article and then click again dislike button we will undo his/her previous dislike
		db.session.delete(already_disliked)
		db.session.commit()
		dislikes = DisLikeArticle.query.filter(DisLikeArticle.article_id == art_id).count()
		likes = LikeArticle.query.filter(LikeArticle.article_id == art_id).count()
		data = {
			"likes": likes,
			"dislikes": dislikes
		}
		return jsonify({'data' : data})
	elif not already_disliked and already_liked:
		# if current_user is already like this article and click dislike button we will delete his/her previous like
		db.session.delete(already_liked)
		db.session.commit()
		dislikes = DisLikeArticle.query.filter(DisLikeArticle.article_id == art_id).count()
		likes = LikeArticle.query.filter(LikeArticle.article_id == art_id).count()
		data = {
			"likes": likes,
			"dislikes": dislikes
		}
		return jsonify({'data' : data})
	else:
		# if current_user didn't like and dislike this article we will record his/her dislike
		dislike = DisLikeArticle(article_id=art_id, author_ip=ip_add)
		db.session.add(dislike)
		db.session.commit()
		dislikes = DisLikeArticle.query.filter(DisLikeArticle.article_id == art_id).count()
		likes = LikeArticle.query.filter(LikeArticle.article_id == art_id).count()
		data = {
			"likes": likes,
			"dislikes": dislikes
		}
		return jsonify({'data' : data})

# ===============================================================================
# 		admin approve subject "root"
# ===============================================================================
@app.route('/Approve_subjects', methods=['GET'])
@login_required
def uprove_subjects():
	# only admin can access this root
	if current_user.usertype == 'Admin':
		subjects = Subject.query.filter(Subject.status != 'Approved')
		return render_template('uprove.html', subjects=subjects)
	else:# if current_user tries to access this root from the url we willl show him/her this message and redirect him/her to home root
		flash('Access Denied', 'danger')
		return redirect(url_for('Subjects'))

# ===============================================================================
#  admin check "subject" before you approve or reject "root"
# ===============================================================================
@app.route('/subject/<int:subject_id>/check', methods=['GET', 'POST'])
@login_required
def check_subject(subject_id):
	# only admin can access this root
	if current_user.usertype == 'Admin':
		subject = Subject.query.get_or_404(subject_id)
		return render_template('check_subject.html', subject=subject)
	else:# if current_user tries to access this root from the url we willl show him/her this message and redirect him/her to home root
		flash('Access Denied', 'danger')
		return redirect(url_for('Subjects'))

# ===============================================================================
# 		admin approve subject "root"
# ===============================================================================
@app.route('/Subject<int:subject_id>/Approve')
@login_required
def approve(subject_id):
	# only admin can access this root
	if current_user.usertype == 'Admin':
		Subject.query.filter(Subject.id == subject_id).update({"status": ('Approved')})
		db.session.commit()
		flash('Subject Approved', 'success')
		return redirect(url_for('Subjects'))
	else:# if current_user tries to access this root from the url we willl show him/her this message and redirect him/her to home root
		flash('Access Denied', 'danger')
		return redirect(url_for('Subjects'))


# ===============================================================================
# 			admin reject subject "root"
# ===============================================================================
@app.route('/Subject/<int:subject_id>/Reject')
@login_required
def reject(subject_id):
	# only admin can access this root
	if current_user.usertype == 'Admin':
		Subject.query.filter(Subject.id == subject_id).update({"status": ('Rejected')})
		db.session.commit()
		flash('Subject Rejected!', 'warning')
		return redirect(url_for('uprove_subjects'))
	else:# if current_user tries to access this root from the url we willl show him/her this message and redirect him/her to home root
		flash('Access Denied', 'danger')
		return redirect(url_for('Subjects'))

# ===============================================================================
# 			home  "root"
# ===============================================================================
@app.route('/')
def Subjects():
	subjects = Subject.query.filter(Subject.status == 'Approved')
	return render_template('index.html', subjects=subjects)

# ===============================================================================
# 		single subject "root"
# ===============================================================================
@app.route('/subject/<int:id>', methods=['POST', 'GET'])
def subject(id):
	subject = Subject.query.get_or_404(id)
	return render_template('subject.html', subject=subject)

# ===============================================================================
# 		create subject "root"
# ===============================================================================
@app.route('/Create_Subject', methods=['POST', 'GET'])
def new_subject():
	form = SubjectForm()
	if form.validate_on_submit():
		subject = Subject(name=form.name.data,purpose=form.purpose.data, authorEmail=form.authorEmail.data)
		db.session.add(subject)
		db.session.commit()
		flash('Subject successfully created!', 'success')
		return redirect(url_for('Subjects'))
	return render_template('new_subject.html', form=form)

# ===============================================================================
# authenticated user edit subject(if user is owner of this subject and subject has no articles) "root"
# ===============================================================================
@app.route('/Subject/<int:subject_id>/Edit', methods=['GET', 'POST'])
@login_required
def update_subject(subject_id):
	form = EditSubjectForm()
	subject = Subject.query.get_or_404(subject_id)
	# only owner of this subject can able to access this root
	if current_user.email == subject.authorEmail:
		if form.validate_on_submit():
			subject.name=form.name.data
			subject.purpose=form.purpose.data
			subject.authorEmail=current_user.email
			subject.status = 'UnApproved'
			db.session.commit()
			flash('Successfully updated', 'success')
			return redirect(url_for('dashboard'))
		elif request.method == 'GET':
			form.name.data=subject.name
			form.purpose.data=subject.purpose
		return render_template('update_subject.html', form=form)
	else:# if current_user tries to access this root from the url we willl show him/her this message and return him/her to home root
		flash('You have no authority to edit subjects other than yours', 'danger')
		return redirect(url_for('Subjects'))

# ===============================================================================
# authenticated user drop subject(if user is owner of this subject and subject has no articles) "root"
# ===============================================================================
@app.route('/Subject/<int:subject_id>/Drop')
@login_required
def drop_subject(subject_id):
	subject = Subject.query.get_or_404(subject_id)
	# only owner of this subject can able to access this root
	if current_user.email == subject.authorEmail:
		if subject.articles.count() > 0:
			flash('This subject has articles. So you can not able to delete', 'warning')
			return redirect(url_for('dashboard'))
		else:
			db.session.delete(subject)
			db.session.commit()
			flash('Subject droped', 'info')
			return redirect(url_for('dashboard'))
	else:# if current_user tries to access this root from the url we willl show him/her this message and return him/her to home root
		flash('You have no authority to delete subjects other than yours', 'danger')
		return redirect(url_for('dashboard'))

# ===============================================================================
# 			view article "root"
# ===============================================================================
@app.route('/article/<int:id>', methods=['POST', 'GET'])
def article(id):
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(content=form.content.data, authorEmail=form.authorEmail.data, article_id=id)
		db.session.add(comment)
		db.session.commit()
		flash('Your comment has published successfully!', 'success')
		return redirect(url_for('article', id=id))
	article = Article.query.get_or_404(id)
	ip_add = request.remote_addr
	visitor = Visitor(article_id=article.id, visitor_ip=ip_add)
	result = Visitor.query.filter(and_(Visitor.article_id == article.id, Visitor.visitor_ip == ip_add)).first()
	if not result:
		db.session.add(visitor)
		db.session.commit()
	return render_template('article.html', article=article, form=form, Comment=Comment, len=len)

# ===============================================================================
# 		save articlefile  "function"
# ===============================================================================
def save_articlefile(article_file):
	if article_file:
		random_hex = secrets.token_hex(8)
		_, f_ext = os.path.splitext(article_file.filename)
		file_fn = random_hex + f_ext
		file_path = os.path.join(app.root_path, 'static/articlefiles', file_fn)
		article_file.save(file_path)# save file to the provided path(file_path)
		return file_fn

# ===============================================================================
# 			create article "root"
# ===============================================================================
@app.route('/Create_Article', methods=['POST', 'GET'])
def New_Article():
	subjects = Subject.query.filter(Subject.status == 'Approved').all()
	subjects_list = [(0, "-- Please select subject --")] + [(i.id, i.name) for i in subjects]
	form = ArticleForm()
	form.subject.choices = subjects_list
	if form.validate_on_submit():
		articlefile = save_articlefile(form.articlefile.data)
		article = Article(title = form.title.data,
			body = form.body.data,
			subject_id=form.subject.data,
			authorEmail = form.authorEmail.data
			) 
		db.session.add(article)
		db.session.commit()
		flash('Article created successfully', 'success')
		return redirect(url_for('Subjects'))
	return render_template('Create_Article.html', form=form, subjects=subjects)

# ===============================================================================
# 			register user "root"
# ===============================================================================
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('Subjects'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_passowrd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_passowrd)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

# ===============================================================================
# 		login user "root"
# ===============================================================================
@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('Subjects'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('Subjects'))
        else:
            flash('Incorrect Email or Passowrd Compination', 'danger')
    return render_template('login.html',form=form)

# ===============================================================================
# 		logout user "root"
# ===============================================================================
@app.route('/logout') 
def logout():
    logout_user()
    return redirect(url_for('Subjects'))

# ===============================================================================
# 				END
# ===============================================================================
