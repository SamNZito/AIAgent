import os
from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from forms import SignUpForm, ProjectStartForm
from models import User, Project  # Import models after db initialization
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from extensions import db, migrate, bcrypt, login_manager  # Import login_manager
import requests

app = Flask(__name__)
app.config.from_object(Config)


# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
login_manager.init_app(app)  # Initialize Flask-Login
login_manager.login_view = "login"  # Redirect users to login if not authenticated


# Configure Upload Folder
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    
    if request.method == "POST":
        print("🚀 Signup form was submitted!")
        print("📩 Raw Form Data:", request.form)  # Print raw data

        if form.validate_on_submit():
            print("✅ Form validation successful!")

            # Check if email already exists
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash("Email is already registered. Please use a different email or log in.", "danger")
                return redirect(url_for('signup'))

            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(name=form.name.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            print(f"📝 User created: {new_user.name}, {new_user.email}")
            flash("Signup successful!", "success")
            return redirect(url_for('project_start'))
        else:
            print("❌ Form validation failed:", form.errors)

    return render_template('signup.html', form=form)


@app.route('/project-start', methods=['GET', 'POST'])
@login_required  # Ensure only logged-in users can start a project
def project_start():
    form = ProjectStartForm()

    if request.method == "POST":
        print("🚀 Project Start form was submitted!")
        print("📩 Raw Form Data:", request.form)

        if form.validate_on_submit():
            print("✅ Form validation successful!")

            resume_filename = None
            if 'resume' in request.files:
                resume_file = request.files['resume']
                if resume_file and allowed_file(resume_file.filename):
                    resume_filename = secure_filename(resume_file.filename)
                    resume_file.save(os.path.join(app.config["UPLOAD_FOLDER"], resume_filename))

            new_project = Project(
                resume=resume_filename,
                linkedIn=form.linkedIn.data,
                job_role=form.job_role.data,
                industry=form.industry.data,
                location=form.location.data,
                work_type=form.work_type.data,
                position_level=form.position_level.data,
                salary=form.salary.data,
                target_company=form.target_company.data,
                user_id=current_user.id  # Link project to the logged-in user
            )

            db.session.add(new_project)
            db.session.commit()

            print(f"📝 Project created: {new_project.job_role}, {new_project.industry} by {current_user.name}")
            flash("Project details saved successfully!", "success")
            return redirect(url_for('projects'))
        else:
            print("❌ Form validation failed:", form.errors)

    return render_template('project_start.html', form=form)



def find_matching_companies(user_project):
    """Query LinkedIn API to find matching companies."""
    
    headers = {
        "Authorization": f"Bearer {current_app.config['LINKEDIN_ACCESS_TOKEN']}",
        "Content-Type": "application/json"
    }

    # LinkedIn API search endpoint (modify based on access level)
    url = "https://api.linkedin.com/v2/organizationSearch"

    params = {
        "q": "industry",
        "industry": user_project.industry,
        "location": user_project.location,
        "work_type": user_project.work_type,
        "limit": 5  # Get top 5 results
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        companies = data.get("elements", [])
        return [
            {
                "name": company.get("name", "Unknown"),
                "industry": company.get("industry", "N/A"),
                "location": company.get("headquarters", {}).get("city", "Unknown"),
                "work_type": user_project.work_type  # No direct mapping, so keeping user's input
            }
            for company in companies
        ]
    else:
        print("LinkedIn API Error:", response.json())
        return []


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("projects"))

        flash("Invalid email or password!", "danger")

    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route('/users')
@login_required
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@app.route('/projects')
@login_required
def projects():
    user_projects = Project.query.filter_by(user_id=current_user.id).all()
    
    project_matches = []
    for project in user_projects:
        matched_companies = find_matching_companies(project)
        project_matches.append({"project": project, "matches": matched_companies})

    return render_template('projects.html', projects=project_matches)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500


if __name__ == '__main__':
    app.run(debug=True)
