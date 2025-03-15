import os
from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from forms import SignUpForm, ProjectStartForm, ResumeUploadForm
from models import User, Project  # Import models after db initialization
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from extensions import db, migrate, bcrypt, login_manager  # Import login_manager
import requests
import shutil

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
    form = ResumeUploadForm()

    if request.method == "POST" and form.validate_on_submit():
        resume_filename = None

        # Handle Resume Upload
        if 'resume' in request.files:
            resume_file = request.files['resume']
            if resume_file and allowed_file(resume_file.filename):
                resume_filename = secure_filename(resume_file.filename)
                resume_file.save(os.path.join(app.config["UPLOAD_FOLDER"], resume_filename))
                current_user.resume = resume_filename  # Save to user profile

        # Update user LinkedIn URL
        current_user.linkedin_url = form.linkedin_url.data
        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for('home'))

    return render_template('home.html', form=form)

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

def generate_modified_resume(original_resume_path, target_company, job_role):
    """
    Simulates AI modifying the resume based on target company and job role.
    For now, it just copies the file with a modified filename.
    """
    modified_resume_filename = f"modified_{target_company.replace(' ', '_')}_{job_role.replace(' ', '_')}.pdf"
    modified_resume_path = os.path.join(app.config["UPLOAD_FOLDER"], modified_resume_filename)
    
    # Simulate AI resume modification (for now, just copying the file)
    shutil.copy(original_resume_path, modified_resume_path)

    return modified_resume_filename  # Return the new resume filename



@app.route('/project-start', methods=['GET', 'POST'])
@login_required
def project_start():
    form = ProjectStartForm()

    if request.method == "POST":
        if form.validate_on_submit():
            selected_industry = form.industry.data
            industry_other = form.industry_other.data if selected_industry == "other" else None

            # Get user's original resume
            original_resume_path = os.path.join(app.config["UPLOAD_FOLDER"], current_user.resume) if current_user.resume else None

            # Generate AI-modified resume
            modified_resume_filename = None
            if original_resume_path:
                modified_resume_filename = generate_modified_resume(original_resume_path, form.target_company.data, form.job_role.data)

            new_project = Project(
                project_name=form.project_name.data,
                job_role=form.job_role.data,
                industry=selected_industry,
                industry_other=industry_other,
                target_location=form.target_location.data,
                work_type=form.work_type.data,
                position_level=form.position_level.data,
                salary_min=form.salary_min.data,
                salary_max=form.salary_max.data,
                target_company=form.target_company.data,
                user_id=current_user.id,
                modified_resume=modified_resume_filename  # 🔹 Store AI-modified resume
            )

            db.session.add(new_project)
            db.session.commit()

            flash("Project created successfully!", "success")
            return redirect(url_for('projects'))
        else:
            flash("Please correct the errors in the form before continuing.", "danger")

    return render_template('project_start.html', form=form)





def find_matching_companies(user_project):
    """Query LinkedIn API to find matching companies."""
    
    headers = {
        "Authorization": f"Bearer {current_app.config.get('LINKEDIN_ACCESS_TOKEN', '')}",
        "Content-Type": "application/json"
    }

    url = "https://api.linkedin.com/v2/organizationSearch"

    params = {
        "q": "industry",
        "industry": user_project.industry,
        "location": user_project.target_location,  # ✅ Fixed: Use "target_location"
        "work_type": user_project.work_type,
        "limit": 5
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
                "work_type": user_project.work_type
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

# @app.route('/projects')
# @login_required
# def projects():
#     user_projects = Project.query.filter_by(user_id=current_user.id).all()
    
#     project_matches = []
#     for project in user_projects:
#         matched_companies = find_matching_companies(project)
#         project_matches.append({"project": project, "matches": matched_companies})

#     return render_template('projects.html', projects=project_matches)

@app.route('/projects')
@login_required
def projects():
    # Get projects created by the logged-in user
    user_projects = Project.query.filter_by(user_id=current_user.id).all()

    return render_template('projects.html', projects=user_projects)



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
