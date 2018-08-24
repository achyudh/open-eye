from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

class SocialIssueInput(FlaskForm):
  social = SelectField("Social Issue",
                        choices=[(0, "Immigration"), (1, "Extremism"), (2, "Gender Equality")],
                        default=0)
  submit = SubmitField("Submit")
class CountryInput(FlaskForm):
  country = StringField("Find Country",
                        default="World")
