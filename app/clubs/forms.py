from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms import StringField, SubmitField
from app.models import User
from flask_wtf import FlaskForm


class ClubForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    submit = SubmitField('Create')