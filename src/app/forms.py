from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import Length

class CreateMemoryForm(FlaskForm):
    prompt = TextAreaField('Prompt', validators=[Length(min=1)])
    answer = TextAreaField('Answer', validators=[Length(min=1)])

class EditMemoryForm(FlaskForm):
    prompt = prompt = TextAreaField('Prompt', validators=[Length(min=1)])
    answer = TextAreaField('Answer', validators=[Length(min=1)])