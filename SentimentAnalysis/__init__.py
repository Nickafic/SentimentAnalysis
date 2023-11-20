from flask import Flask 
from .views import views
from .auth import auth

UPLOADPATH = "./TEMP/"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'klkl dkjkjfi'

    #Set The Path To The UPLOAD FOLDER
    app.config['UPLOAD_FOLDER'] = UPLOADPATH
    
    # Set the maximum file size to 4 megabytes
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024   # 4 MB

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app