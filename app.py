"""
Aeroponik Dashboard — FastAPI Application

Main application file with all routes for the Aeroponik monitoring dashboard.
Migrated from Flask to FastAPI per PRD specifications.
"""
import os
from datetime import datetime, date
from pathlib import Path

from fastapi import FastAPI, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import BaselineIdeal, LogHarian, BatchTanam

# ─── App Setup ───
app = FastAPI(
    title="Aeroponik Dashboard",
    description="Buku Saku Digital untuk pemantauan tanaman aeroponik",
    version="2.0.0"
)

# Static files & templates
BASE_DIR = Path(__file__).resolve().parent

if os.environ.get("VERCEL"):
    UPLOAD_DIR = Path("/tmp/uploads")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="static_uploads")
else:
    UPLOAD_DIR = BASE_DIR / "static" / "uploads"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Max upload size: 16MB (enforced at proxy level in production)
MAX_UPLOAD_SIZE = 16 * 1024 * 1024


# ─── Startup Event ───
@app.on_event("startup")
def on_startup():
    """Create tables on startup if they don't exist."""
    if not os.environ.get("VERCEL"):
        os.makedirs("instance", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed baseline data
    from seed import seed_data
    seed_data()


# ─── Scoring Logic ───
def calculate_score(tinggi: float, daun: int, hari_ke: int, db: Session) -> tuple[float, str]:
    """Calculate composite growth score (0-100) and category.
    
    Score = average of (tinggi_ratio, daun_ratio) * 100
    Thresholds per PRD:
      >= 80 → Hijau (Optimal)
      >= 50 → Kuning (Perhatian)
      <  50 → Merah (Kritis)
    
    Args:
        tinggi: Measured height in cm.
        daun: Measured leaf count.
        hari_ke: Day number in the growth cycle.
        db: Database session.
    
    Returns:
        Tuple of (numeric_score, category_label).
    """
    baseline = db.query(BaselineIdeal).filter_by(
        hari_ke=hari_ke, media_tanam='rockwool'
    ).first()

    if baseline:
        ideal_tinggi = baseline.ideal_tinggi
        ideal_daun = baseline.ideal_daun
    else:
        # Fallback for days beyond 29 — extrapolate from last known baseline
        last = db.query(BaselineIdeal).filter_by(
            media_tanam='rockwool'
        ).order_by(BaselineIdeal.hari_ke.desc()).first()
        if last:
            # Simple linear extrapolation from last data point
            extra_days = hari_ke - last.hari_ke
            ideal_tinggi = last.ideal_tinggi + (extra_days * 2.0)
            ideal_daun = last.ideal_daun + (extra_days * 1)
        else:
            # Absolute fallback
            ideal_tinggi = 2.0 + (hari_ke * 0.8)
            ideal_daun = 2 + (hari_ke // 3)

    tinggi_ratio = tinggi / ideal_tinggi if ideal_tinggi > 0 else 1.0
    daun_ratio = daun / ideal_daun if ideal_daun > 0 else 1.0

    # Composite score: 0-100 (capped at 100)
    skor = min(100.0, ((tinggi_ratio + daun_ratio) / 2.0) * 100)

    # Category based on PRD thresholds
    if skor >= 80:
        kategori = 'Hijau'
    elif skor >= 50:
        kategori = 'Kuning'
    else:
        kategori = 'Merah'

    return round(skor, 1), kategori


# ═══════════════════════════════════════════════════
#  PAGE ROUTES (HTML)
# ═══════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    """Landing page — introduces the project and gives clear CTA."""
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/catat", response_class=HTMLResponse)
def catat(request: Request, batch_id: int = None, db: Session = Depends(get_db)):
    """Daily log form with batch selector."""
    active_batches = db.query(BatchTanam).filter_by(status='aktif').order_by(
        BatchTanam.created_at.desc()
    ).all()
    return templates.TemplateResponse("catat.html", {
        "request": request,
        "batches": active_batches,
        "preselected_batch_id": batch_id,
    })


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    """Help / guide page."""
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/logs", response_class=HTMLResponse)
def logs(request: Request, batch_id: int = None, db: Session = Depends(get_db)):
    """Log history page, optionally filtered by batch."""
    query = db.query(LogHarian).order_by(LogHarian.created_at.desc())
    
    if batch_id:
        query = query.filter_by(batch_id=batch_id)
    
    all_logs = query.all()
    all_batches = db.query(BatchTanam).order_by(BatchTanam.created_at.desc()).all()
    
    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": all_logs,
        "batches": all_batches,
        "selected_batch_id": batch_id,
    })


@app.get("/batches", response_class=HTMLResponse)
def batches_page(request: Request, db: Session = Depends(get_db)):
    """Batch management page."""
    all_batches = db.query(BatchTanam).order_by(BatchTanam.created_at.desc()).all()
    return templates.TemplateResponse("batches.html", {
        "request": request,
        "batches": all_batches,
    })


# ═══════════════════════════════════════════════════
#  API ROUTES (JSON)
# ═══════════════════════════════════════════════════

@app.post("/api/batch", response_class=JSONResponse)
def create_batch(
    nama_batch: str = Form(...),
    tanggal_mulai: str = Form(...),
    nozzle_size: float = Form(0.1),
    media_tanam: str = Form('rockwool'),
    db: Session = Depends(get_db)
):
    """Create a new planting batch."""
    try:
        parsed_date = datetime.strptime(tanggal_mulai, "%Y-%m-%d").date()
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Format tanggal tidak valid. Gunakan YYYY-MM-DD."}
        )
    
    batch = BatchTanam(
        nama_batch=nama_batch,
        nozzle_size=nozzle_size,
        media_tanam=media_tanam,
        tanggal_mulai=parsed_date,
        status='aktif'
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    return {
        "status": "success",
        "message": f"Batch '{nama_batch}' berhasil dibuat.",
        "batch_id": batch.id
    }


@app.post("/api/batch/{batch_id}/close", response_class=JSONResponse)
def close_batch(batch_id: int, db: Session = Depends(get_db)):
    """Mark a batch as completed."""
    batch = db.query(BatchTanam).filter_by(id=batch_id).first()
    if not batch:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Batch tidak ditemukan."})
    
    batch.status = 'selesai'
    db.commit()
    
    return {"status": "success", "message": f"Batch '{batch.nama_batch}' ditandai selesai."}


@app.post("/submit_log", response_class=JSONResponse)
async def submit_log(
    batch_id: int = Form(...),
    hari_ke: int = Form(...),
    tinggi: float = Form(...),
    daun: int = Form(...),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Submit a daily observation log for a batch."""
    try:
        # Validate batch exists and is active
        batch = db.query(BatchTanam).filter_by(id=batch_id).first()
        if not batch:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Batch tidak ditemukan."}
            )
        if batch.status != 'aktif':
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Batch sudah selesai, tidak bisa menambah log."}
            )

        # Calculate score
        skor_numerik, skor_kategori = calculate_score(tinggi, daun, hari_ke, db)

        # Save photo
        path_foto = None
        if foto and foto.filename:
            # Sanitize filename
            safe_name = foto.filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_filename = f"{batch_id}_{hari_ke}_{timestamp}_{safe_name}"
            filepath = UPLOAD_DIR / unique_filename
            
            content = await foto.read()
            if len(content) > MAX_UPLOAD_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"status": "error", "message": "Ukuran file terlalu besar (maks 16MB)."}
                )
            
            with open(filepath, "wb") as f:
                f.write(content)
            path_foto = f"uploads/{unique_filename}"

        # Save to DB
        log = LogHarian(
            batch_id=batch_id,
            hari_ke=hari_ke,
            tinggi=tinggi,
            daun=daun,
            skor_numerik=skor_numerik,
            skor_sistem=skor_kategori,
            path_foto=path_foto
        )
        db.add(log)
        db.commit()

        return {
            "status": "success",
            "skor": skor_kategori,
            "skor_numerik": skor_numerik,
            "message": "Data berhasil disimpan."
        }

    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.get("/api/batch/{batch_id}/hari_ke", response_class=JSONResponse)
def get_hari_ke(batch_id: int, db: Session = Depends(get_db)):
    """Get the current day number for a batch (auto-calculated from start date)."""
    batch = db.query(BatchTanam).filter_by(id=batch_id).first()
    if not batch:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Batch tidak ditemukan."})
    
    return {
        "status": "success",
        "hari_ke": batch.hari_ke_hari_ini(),
        "tanggal_mulai": batch.tanggal_mulai.isoformat(),
        "nama_batch": batch.nama_batch,
        "nozzle_size": batch.nozzle_size,
        "media_tanam": batch.media_tanam,
    }


# ─── Run with Uvicorn ───
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
