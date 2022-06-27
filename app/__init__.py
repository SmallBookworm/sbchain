from flask import Flask

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'E:\\'
app.secret_key = "affedasafafqwerwet345436ewf23dfsd"
from app import views