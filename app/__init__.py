import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)

    # Security / forms
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')

    # Database
    instance_path = os.path.join(app.root_path, '..', 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, 'water_it.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Uploads
    upload_dir = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_dir
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    # Weather
    app.config['OPENWEATHER_API_KEY'] = os.getenv('OPENWEATHER_API_KEY', '')
    app.config['DEFAULT_CITY'] = os.getenv('DEFAULT_CITY', 'San Francisco')

    db.init_app(app)
    csrf.init_app(app)

    # Models
    from . import models  # noqa: F401

    with app.app_context():
        db.create_all()

        # Lightweight SQLite migrations for older DBs
        from .db_migrate import run_sqlite_migrations
        run_sqlite_migrations(db)

        # Backfill next_run_at for older reminders
        from .models import Reminder
        from .notifications import compute_next_run
        from datetime import datetime
        now = datetime.utcnow()
        old = Reminder.query.filter((Reminder.next_run_at.is_(None))).all()
        for rem in old:
            start = rem.start_date or now.date()
            rem.next_run_at = compute_next_run(rem.interval_text, rem.time_of_day, start=start, now=now)
        if old:
            db.session.commit()

    # Blueprints
    from .blueprints.home.routes import bp as home_bp
    from .blueprints.plants.routes import bp as plants_bp
    from .blueprints.settings.routes import bp as settings_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(plants_bp, url_prefix='/plants')
    app.register_blueprint(settings_bp, url_prefix='/settings')

    from .blueprints.push import bp as push_bp
    app.register_blueprint(push_bp, url_prefix='/push')

    # Scheduler: check due reminders and send web-push notifications.
    scheduler = BackgroundScheduler(daemon=True)

    from .notifications import tick_reminders

    def _job():
        with app.app_context():
            tick_reminders()

    scheduler.add_job(_job, 'interval', seconds=60, id='tick_reminders', replace_existing=True)
    scheduler.start()

    # Jinja helpers
    @app.template_filter('nl2br')
    def nl2br(s: str):
        return (s or '').replace('\n', '<br>')

    return app
