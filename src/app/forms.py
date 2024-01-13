from flask_wtf import FlaskForm
from wtforms import TextAreaField, RadioField
from wtforms.validators import Length

class CreateMemoryForm(FlaskForm):
    prompt = TextAreaField('Prompt', validators=[Length(min=1, message="Prompt is required")])
    answer = TextAreaField('Answer', validators=[Length(min=1, message="Answer is required")])

class EditMemoryForm(FlaskForm):
    prompt = prompt = TextAreaField('Prompt', validators=[Length(min=1, message="Prompt is required")])
    answer = TextAreaField('Answer', validators=[Length(min=1, message="Answer is required")])
    status = RadioField('Status', choices=[('active', 'Active'), ('inactive', 'Inactive'), ('completed', 'Complete')])

class SubmitTestForm(FlaskForm):
    result = RadioField('Result', choices=[('perfect', 'Perfect Recall'), ('partial', 'Partial Recall'), ('failed', 'Failed Recall')])