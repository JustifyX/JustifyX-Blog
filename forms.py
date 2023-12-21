from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields import StringField, SubmitField, PasswordField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, ValidationError
from werkzeug.utils import secure_filename
from PIL import Image


class AddBlogForm(FlaskForm):
    name = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    post_date = DateField('Post Date', validators=[DataRequired()], format='%Y-%m-%d')
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    description = StringField('Description', validators=[DataRequired(), Length(min=2, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_image(self, field):
        if field.data:
            filename = secure_filename(field.data.filename)
            allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}

            if '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                image = Image.open(field.data)
                width, height = image.size

                if width != 1270 or height != 400:
                    raise ValidationError('Image must have dimensions of 1270x400 pixels.')
            else:
                raise ValidationError('Invalid file format. Allowed formats: jpg, jpeg, png, gif.')
class RegisterForm(FlaskForm):
    email = StringField(
                        validators=[DataRequired(message="Email field is mandatory")])
    username = StringField(
                           validators=[DataRequired(message="Username field is mandatory")])
    password = PasswordField(validators=[DataRequired(message="Password field is mandatory")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField("Login")

class CommentForm(FlaskForm):
    comment = TextAreaField("Add a Comment", validators=[DataRequired(message="Comment field is mandatory")])
    submit_comment = SubmitField("Submit Comment")

class SearchForm(FlaskForm):
    search = StringField("Search", render_kw={"placeholder": "Search..."}, id="search-input")
    submit = SubmitField("Go")