from flask import Flask
from flask_cors import CORS
from .config import Config
from .modules.health.routes import health_bp
from .modules.tts.routes import tts_bp


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # 注册蓝图
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(tts_bp, url_prefix='/api/v1')

    return app
