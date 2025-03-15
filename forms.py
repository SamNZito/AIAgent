from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SelectField, SubmitField, DecimalField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Email, Length, Regexp, URL, Optional, NumberRange

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
    project_name = StringField("Project Name", validators=[DataRequired()],
                               render_kw={"placeholder": "Name your job hunt project"})

    job_role = StringField("Target Job Role", validators=[DataRequired()],
                           render_kw={"placeholder": "e.g. UX Designer"})

    industry = SelectField("Target Industry", choices=[
        ("technology", "Technology"),
        ("finance", "Finance"),
        ("healthcare", "Healthcare"),
        ("marketing", "Marketing"),
        ("education", "Education"),
        ("engineering", "Engineering"),
        ("consulting", "Consulting"),
        ("other", "Other")  # "Other" option added
    ], validators=[DataRequired()])

    industry_other = StringField("Specify Industry (if 'Other')", validators=[Optional()],
                                 render_kw={"placeholder": "Enter your industry"})

    target_location = StringField("Target Location", validators=[DataRequired()],
                                  render_kw={"placeholder": "City, Country"})

    work_type = RadioField("Work Type", choices=[
        ("Remote", "Remote"),
        ("Hybrid", "Hybrid"),
        ("On-Site", "On-Site")
    ], validators=[DataRequired()])

    position_level = SelectField("Position Level", choices=[
        ("Intern", "Intern"),
        ("Junior", "Junior"),
        ("Mid", "Mid-Level"),
        ("Senior", "Senior"),
        ("Manager", "Manager"),
        ("Director", "Director"),
        ("VP", "VP"),
        ("C-Level", "C-Level")
    ], validators=[DataRequired()])

    salary_min = DecimalField("Min Salary", validators=[DataRequired(), NumberRange(min=0)], 
                              render_kw={"placeholder": "Min"})

    salary_max = DecimalField("Max Salary", validators=[DataRequired(), NumberRange(min=0)], 
                              render_kw={"placeholder": "Max"})

    target_company = TextAreaField("Desired Companies", validators=[DataRequired()],
                                   render_kw={"placeholder": "Describe your ideal companies"})

    submit = SubmitField("Continue")