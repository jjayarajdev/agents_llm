from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from celery import Celery
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

db = SQLAlchemy()

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    Migrate(app, db)
    Limiter(app, key_func=get_remote_address)
    CORS(app)

    with app.app_context():
        from app import models, routes, admin, auth, chain
        db.create_all()
        app.register_blueprint(routes.bp, url_prefix="/api/v1")
        app.register_blueprint(admin.admin_bp, url_prefix="/api/v1/admin")
        app.register_blueprint(auth.auth_bp, url_prefix="/api/v1/auth")
        app.register_blueprint(chain.chain_bp, url_prefix="/api/v1/chain")
    
    return app

app = create_app()
celery = make_celery(app)
