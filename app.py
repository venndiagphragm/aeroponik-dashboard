import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from models import db, BaselineIdeal, LogHarian
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bayamin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB max upload

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logs')
def logs():
    # Order by created_at descending
    all_logs = LogHarian.query.order_by(LogHarian.created_at.desc()).all()
    return render_template('logs.html', logs=all_logs)

@app.route('/submit_log', methods=['POST'])
def submit_log():
    try:
        hari_ke = int(request.form.get('hari_ke', 1))
        tinggi = float(request.form.get('tinggi', 0))
        daun = int(request.form.get('daun', 0))
        foto = request.files.get('foto')

        # Baseline Calculation
        baseline = BaselineIdeal.query.filter_by(hari_ke=hari_ke).first()
        if not baseline:
            # Fallback if baseline doesn't exist
            ideal_tinggi = 2.0 + (hari_ke * 0.8)
            ideal_daun = 2 + (hari_ke // 3)
        else:
            ideal_tinggi = baseline.ideal_tinggi
            ideal_daun = baseline.ideal_daun

        # Calculate Score
        # Simple Logic: Avg of (tinggi/ideal_tinggi) and (daun/ideal_daun)
        tinggi_ratio = tinggi / ideal_tinggi if ideal_tinggi > 0 else 1
        daun_ratio = daun / ideal_daun if ideal_daun > 0 else 1
        avg_ratio = (tinggi_ratio + daun_ratio) / 2.0

        if avg_ratio >= 0.9:
            skor = 'Hijau'
        elif avg_ratio >= 0.7:
            skor = 'Kuning'
        else:
            skor = 'Merah'

        # Save Foto
        path_foto = None
        if foto and foto.filename:
            filename = secure_filename(foto.filename)
            # Make unique filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_filename = f"{hari_ke}_{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            foto.save(filepath)
            path_foto = f"uploads/{unique_filename}"

        # Save to DB
        log = LogHarian(
            hari_ke=hari_ke,
            tinggi=tinggi,
            daun=daun,
            skor_sistem=skor,
            path_foto=path_foto
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'skor': skor,
            'message': 'Data berhasil disimpan.'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
