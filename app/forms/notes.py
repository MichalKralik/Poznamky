from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import current_app

class CreateNoteForm(FlaskForm):
    content = TextAreaField('Note Content', validators=[DataRequired()])
    expiration = SelectField('Expires After', choices=[
        ('hour', '1 Hour'),
        ('day', '1 Day'),
        ('week', '1 Week'),
        ('never', 'Never')
    ], default='day')
    is_one_time = BooleanField('Self-destruct after reading')
    submit = SubmitField('Save Note')
