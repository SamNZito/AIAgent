import os
import ollama  # Import Ollama API client
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# -------------------------------
# Function to call Ollama's API to generate a message
def generate_message_olama(prompt):
    """Fetch response from Ollama API."""
    try:
        response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
        return response['message']['content'].strip() if 'message' in response else "Error: No valid response."
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------
# Function to construct a structured prompt for Ollama
def generate_outreach_prompt(candidate_name, candidate_background, company_name, hiring_manager_name, company_challenge):
    """Create a structured prompt for outreach message generation."""
    return f"""
    You are a career coach helping a candidate craft a compelling introductory outreach message.
    
    Candidate Information:
    - Name: {candidate_name}
    - Background: {candidate_background}
    
    Target Company:
    - Name: {company_name}
    - Hiring Manager: {hiring_manager_name}
    - Company Challenge: {company_challenge}
    
    Task: 
    - Write a professional, engaging email for {candidate_name} to send to {hiring_manager_name} at {company_name}.
    - Reference the company’s challenge of {company_challenge} and explain how {candidate_name}'s expertise can help.
    - Keep the message concise (around 5 sentences) and formal.
    """

# -------------------------------
@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

# -------------------------------
@app.route('/generate_message', methods=['POST'])
def generate_message():
    """Generate an outreach message using the Ollama API."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request, JSON expected"}), 400
        
        candidate_name = data.get('candidate_name', "a candidate")
        candidate_background = data.get('candidate_background', "a professional")
        company_name = data.get('company_name', "a company")
        hiring_manager_name = data.get('hiring_manager_name', "a hiring manager")
        company_challenge = data.get('company_challenge', "some challenges")

        if not all([candidate_name, candidate_background, company_name, hiring_manager_name, company_challenge]):
            return jsonify({"error": "Missing required fields"}), 400

        prompt = generate_outreach_prompt(candidate_name, candidate_background, company_name, hiring_manager_name, company_challenge)
        message = generate_message_olama(prompt)
        
        return jsonify({"message": message})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
