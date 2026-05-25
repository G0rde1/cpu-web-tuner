from flask import Flask
from flask_socketio import SocketIO
import os

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-12345')
    app.config['DATA_DIR'] = os.path.expanduser('~/.cpu-web-tuner')
    
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    os.makedirs(f"{app.config['DATA_DIR']}/logs", exist_ok=True)
    
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    socketio.init_app(app)
    return app