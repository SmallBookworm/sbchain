import secrets
from flask import Flask

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'E:\\'
app.config['DOWNLOAD_FOLDER'] = 'C:\\Users\\60514\\Desktop\\'
app.secret_key = secrets.token_urlsafe(32)
from app import views