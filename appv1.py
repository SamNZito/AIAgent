import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

# Configure database (here we use SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///boss_hunter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set your OpenAI API key as an environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# A simple User model (expand as needed for multi-tenancy and secure authentication)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # In production, NEVER store plain-text passwords. Use proper hashing.
    password = db.Column(db.String(120), nullable=False)
    candidate_name = db.Column(db.String(120), nullable=True)

# Home page to serve our HTML frontend
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to generate outreach messages
@app.route('/generate_message', methods=['POST'])
def generate_message():
    data = request.json

    candidate_name = data.get('candidate_name')
    candidate_background = data.get('candidate_background')
    company_name = data.get('company_name')
    hiring_manager_name = data.get('hiring_manager_name')
    company_challenge = data.get('company_challenge')

    # Construct a prompt for the language model
    prompt = (
        f"Draft a compelling introductory email from {candidate_name}, who has a background in {candidate_background}, "
        f"addressed to {hiring_manager_name} at {company_name}. The email should reference the challenge of "
        f"{company_challenge} and explain how the candidate's expertise can help solve it. Keep the tone professional "
        "and engaging."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert career coach drafting personalized outreach emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        message = response['choices'][0]['message']['content']
        return jsonify({"message": message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)