from datetime import datetime
from . import db


class Plant(db.Model):
    __tablename__ = 'plants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    scientific_name = db.Column(db.String(200), nullable=True)
    origin = db.Column(db.String(200), nullable=True)
    age_months = db.Column(db.Integer, nullable=True)

    light = db.Column(db.String(120), nullable=True)   # e.g. Bright indirect
    water = db.Column(db.String(120), nullable=True)   # e.g. Moderate
    soil = db.Column(db.String(200), nullable=True)    # e.g. Airy and slightly acidic

    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    photos = db.relationship('PlantPhoto', backref='plant', cascade='all, delete-orphan', lazy=True)
    reminders = db.relationship('Reminder', backref='plant', cascade='all, delete-orphan', lazy=True)


class PlantPhoto(db.Model):
    __tablename__ = 'plant_photos'

    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Reminder(db.Model):
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), nullable=False)

    # Store as simple text like "2 weeks" and time like "09:00" for now.
    interval_text = db.Column(db.String(80), nullable=False)  # e.g. "2 weeks"
    time_of_day = db.Column(db.String(10), nullable=False)    # e.g. "09:00"
    start_date = db.Column(db.Date, nullable=True)

    # Notification scheduling
    active = db.Column(db.Boolean, default=True)
    next_run_at = db.Column(db.DateTime, nullable=True)
    last_sent_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PushSubscription(db.Model):
    __tablename__ = 'push_subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.Text, nullable=False, unique=True)
    p256dh = db.Column(db.Text, nullable=False)
    auth = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
