from extensions import db, bcrypt
from flask_login import UserMixin

class User(db.Model, UserMixin):  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    resume = db.Column(db.String(255), nullable=True)  # 🔹 Store resume file path
    linkedin_url = db.Column(db.String(255), nullable=True)  # 🔹 Store LinkedIn URL

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modified_resume = db.Column(db.String(255), nullable=True)  # 🔹 Store AI-modified resume per project

    project_name = db.Column(db.String(150), nullable=False)
    job_role = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    industry_other = db.Column(db.String(100), nullable=True)  # 🔹 NEW: Stores user-entered industry if "Other" is selected
    target_location = db.Column(db.String(200), nullable=False)  # 🔹 Renamed from `location`

    work_type = db.Column(db.Enum("Remote", "Hybrid", "On-Site", name="work_type_enum"), nullable=False)
    position_level = db.Column(db.String(50), nullable=False)

    salary_min = db.Column(db.Numeric(10, 2), nullable=True)  # 🔹 Replacing `salary`
    salary_max = db.Column(db.Numeric(10, 2), nullable=True)

    target_company = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
