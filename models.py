from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, date

from database import Base


class BatchTanam(Base):
    """Represents a planting batch/cycle.
    
    Each batch tracks a single planting cycle with its specific
    nozzle size, growing media, and start date. All daily logs
    are associated with a specific batch.
    """
    __tablename__ = 'batch_tanam'

    id = Column(Integer, primary_key=True, index=True)
    nama_batch = Column(String(100), nullable=False)        # e.g. "Batch Bayam #1"
    nozzle_size = Column(Float, nullable=False, default=0.1) # mm — hanya 0.1mm untuk saat ini
    media_tanam = Column(String(50), nullable=False, default='rockwool')
    tanggal_mulai = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default='aktif')  # "aktif" | "selesai"
    created_at = Column(DateTime, default=datetime.utcnow)

    logs = relationship('LogHarian', back_populates='batch', lazy='dynamic',
                        order_by='LogHarian.hari_ke')

    def hari_ke_hari_ini(self) -> int:
        """Calculate which day of the cycle today is."""
        delta = date.today() - self.tanggal_mulai
        return max(1, delta.days + 1)  # Day 1 = tanggal_mulai


class LogHarian(Base):
    """Daily observation log for a specific batch.
    
    Records height, leaf count, photo, and calculated composite score.
    Always linked to a BatchTanam via batch_id.
    """
    __tablename__ = 'log_harian'

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey('batch_tanam.id'), nullable=False)
    hari_ke = Column(Integer, nullable=False)
    tinggi = Column(Float, nullable=False)        # cm
    daun = Column(Integer, nullable=False)         # helai
    skor_numerik = Column(Float, nullable=True)    # composite score 0-100
    skor_sistem = Column(String(50), nullable=False)  # Hijau, Kuning, Merah
    path_foto = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship('BatchTanam', back_populates='logs')


class BaselineIdeal(Base):
    """Ideal growth targets per day, derived from research paper data.
    
    Data source: nozzle 0.1mm + rockwool growing media.
    Values for odd days come directly from paper measurements;
    even days are linearly interpolated between adjacent data points.
    """
    __tablename__ = 'baseline_ideal'

    id = Column(Integer, primary_key=True, index=True)
    hari_ke = Column(Integer, nullable=False)
    media_tanam = Column(String(50), nullable=False, default='rockwool')
    ideal_tinggi = Column(Float, nullable=False)   # cm
    ideal_daun = Column(Integer, nullable=False)    # helai

    __table_args__ = (
        UniqueConstraint('hari_ke', 'media_tanam', name='uq_hari_media'),
    )
