import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # LinkedIn API Credentials
    LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "78m5r47pulvdyy")
    LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "WPL_AP1.SYVEeWYvXVost9PW.OEt/xg==")
    LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "your_access_token")
