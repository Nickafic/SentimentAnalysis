from flask import Flask, render_template, session 
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

    @app.errorhandler(413)
    def handle_request_entity_too_large(error):
        return render_template('main.html', USERNAME=session["username"], ERRORMESSAGE="(413)File size exceeds the allowed limit")


    return app
