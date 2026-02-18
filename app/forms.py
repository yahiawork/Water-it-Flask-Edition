from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class PlantForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    scientific_name = StringField('Scientific', validators=[Optional(), Length(max=200)])
    origin = StringField('Origin', validators=[Optional(), Length(max=200)])
    age_months = IntegerField('Age (months)', validators=[Optional(), NumberRange(min=0, max=600)])

    light = StringField('Light', validators=[Optional(), Length(max=120)])
    water = StringField('Water', validators=[Optional(), Length(max=120)])
    soil = StringField('Soil', validators=[Optional(), Length(max=200)])

    notes = TextAreaField('Notes', validators=[Optional(), Length(max=4000)])

    photos = MultipleFileField('Photos')

    submit = SubmitField('Save')


class ReminderForm(FlaskForm):
    interval_text = StringField('Interval', validators=[DataRequired(), Length(max=80)])
    time_of_day = StringField('Time', validators=[DataRequired(), Length(max=10)])
    submit = SubmitField('Add')
