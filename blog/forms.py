from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from blog.modules import User, Article, Comment, Subject


# ===============================================================================
# 		Creating new subject "Form"
# ===============================================================================
class SubjectForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired(), Length(min=5, max=30)])
	authorEmail = StringField('AuthorEmail', validators=[DataRequired(), Email()])
	purpose = TextAreaField('Purpose', validators=[DataRequired(), Length(min=100)])
	submit = SubmitField('Create')

	# ===============================================================================
	# 			Avoid duplicate subject name "function"
	# ===============================================================================
	def validate_name(self, name):
		result = Subject.query.filter(Subject.name == name.data).first()
		if result:
			raise ValidationError('This subject is already exists.')

# ===============================================================================
# 			Editing subject "Form"
# ===============================================================================
class EditSubjectForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired(), Length(min=5, max=30)])
	purpose = TextAreaField('Purpose', validators=[DataRequired(), Length(min=100)])
	submit = SubmitField('Update')

# ===============================================================================
# 			Creating new article "Form"
# ===============================================================================
class ArticleForm(FlaskForm):
	subject = SelectField('Select Subject', coerce=int, validators=[DataRequired()])
	title = StringField('Article Tilte', validators=[DataRequired(), Length(min=15, max=45)])
	body = TextAreaField('Article Body', validators=[DataRequired(), Length(min=100, max=500)])
	articlefile = FileField('Article File', validators=[DataRequired(), FileAllowed(['png', 'jpg', 'jpeg', 'pdf'])])
	authorEmail = StringField('AuthorEmail', validators=[DataRequired(),Email()])
	submit = SubmitField('Post')

	# ===============================================================================
	# 			Avoid duplicate article name "function"
	# ===============================================================================
	def validate_title(self, title):
		result = Article.query.filter(Article.title == title.data).first()
		if result:
			raise ValidationError('This title is already posted.')

# ===============================================================================
# 			Comment "Form"
# ===============================================================================
class CommentForm(FlaskForm):
	content = TextAreaField('Comment Content', validators=[DataRequired('Content field is Empty'), Length(min=3)])
	authorEmail = StringField('Email Address', validators=[DataRequired(), Email()])
	submit = SubmitField('Post Comment')

	# ===============================================================================
	# 		validate comment content  "function"
	# ===============================================================================
	def validate_content(self, content):
		improper_words = ['Stupid', 'F*ck', 'F*ck you', 'Shit', 'Piss off',
		'Dick head', 'Asshole', 'Son of a b*tch', 'Bastard', 'Bitch',
		'Damn', 'C*nt', 'Bollocks', 'Bugger', 'Bloody Hell', 'Choad', 'Fuck off', 'Illiterate']
		for iw in improper_words:
			if content.data.find(iw) > -1:
				raise ValidationError('Our system does not support commenting with improper words please try to use polite words')

# ===============================================================================
# 			User Registration "Form"
# ===============================================================================
class RegistrationForm(FlaskForm):
	username = StringField('UserName', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('ConfirmPassword', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Create Account')

	# ===============================================================================
	# validate user's email is already in our system when he/she try to register "function"
	# ===============================================================================
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('This emaill is alrealy exist in our system please choose another email')

# ===============================================================================
# 			User login "Form"
# ===============================================================================
class LoginForm(FlaskForm):
   email = StringField('Email',
   	      validators=[DataRequired(),Email()])
   password = PasswordField('Password',
   	       validators=[DataRequired()] )
   submit = SubmitField('Login')

# ===============================================================================
# 					END
# ===============================================================================
