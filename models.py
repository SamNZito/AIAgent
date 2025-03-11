from extensions import db, bcrypt
from flask_login import UserMixin

class User(db.Model, UserMixin):  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume = db.Column(db.String(255), nullable=True)  # Store file path
    linkedIn = db.Column(db.String(255), nullable=True)
    job_role = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    work_type = db.Column(db.String(50), nullable=False)
    position_level = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.String(50), nullable=True)
    target_company = db.Column(db.Text, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # Links project to a user
