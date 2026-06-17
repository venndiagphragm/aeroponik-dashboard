from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BaselineIdeal(db.Model):
    __tablename__ = 'baseline_ideal'
    
    id = db.Column(db.Integer, primary_key=True)
    hari_ke = db.Column(db.Integer, unique=True, nullable=False)
    ideal_tinggi = db.Column(db.Float, nullable=False)
    ideal_daun = db.Column(db.Integer, nullable=False)

class LogHarian(db.Model):
    __tablename__ = 'log_harian'
    
    id = db.Column(db.Integer, primary_key=True)
    hari_ke = db.Column(db.Integer, nullable=False)
    tinggi = db.Column(db.Float, nullable=False)
    daun = db.Column(db.Integer, nullable=False)
    skor_sistem = db.Column(db.String(50), nullable=False) # Hijau, Kuning, Merah
    path_foto = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
