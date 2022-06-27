import secrets
from flask import Flask

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'E:\\'
app.secret_key = secrets.token_urlsafe(32)
from app import views