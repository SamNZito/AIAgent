from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, URL, Optional

class SignUpForm(FlaskForm):
    name = StringField("Name", validators=[
        DataRequired(),
        Regexp("^[a-zA-Z\s'-]+$", message="Name must contain only letters and spaces.")
    ])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters."),
        Regexp(r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])', message="Password must contain uppercase, lowercase, number, and special character.")
    ])
    submit = SubmitField("Sign Up")

class OptionalURLField(StringField):
    """Custom field to handle empty LinkedIn input properly."""
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].strip()
            if not self.data:  # Convert empty string to None
                self.data = None

class ProjectStartForm(FlaskForm):
    resume = FileField("Upload Resume (PDF, DOC, DOCX)")
    linkedIn = OptionalURLField("LinkedIn Profile (Optional)", validators=[Optional(), URL()])
    job_role = StringField("Desired Job Role", validators=[DataRequired()])
    industry = StringField("Industry Preferences", validators=[DataRequired()])
    location = StringField("Location (City, State, Zip)", validators=[DataRequired()])
    work_type = SelectField("Work Type", choices=[("Remote", "Remote"), ("Hybrid", "Hybrid"), ("Onsite", "Onsite")])
    position_level = SelectField("Position Level", choices=[
        ("IC", "Individual Contributor"),
        ("Manager", "Manager"),
        ("Director", "Director"),
        ("VP", "VP"),
        ("C-Level", "C-Level")
    ])
    salary = StringField("Salary Expectations")
    target_company = StringField("Target Company Description")
    submit = SubmitField("Save Project Details")
