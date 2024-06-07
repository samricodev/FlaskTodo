import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = "12345" #Secret Key
    
    app.config.from_mapping(
        SECRET_KEY = 'mikey',
        DATABASE_HOST = os.environ.get('FLASK_DATABASE_HOST'),
        DATABASE_PASSWORD = os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE_USER = os.environ.get('FLASK_DATABASE_USER'),
        DATABASE = os.environ.get('FLASK_DATABASE'),
        EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS'),
        EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    )

    from . import db

    db.init_app(app)

    from . import auth
    from . import todo
    from . import admin

    app.register_blueprint(auth.bp)
    app.register_blueprint(todo.bp)
    app.register_blueprint(admin.bp)

    @app.route('/hola') 
    def hola():
        return 'Hola Mundo'
    

    return app
