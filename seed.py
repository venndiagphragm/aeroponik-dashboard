"""
Seed script for Aeroponik Dashboard.

Populates baseline_ideal table with growth curve data derived from
research paper measurements (nozzle 0.1mm + rockwool media).

Data points at odd days (1,3,5,...,29) are from the paper.
Even days (2,4,6,...,28) are linearly interpolated between adjacent measurements.
Leaf count for days 19-29 estimated from observed exponential trend.
"""
import os
import math
from database import engine, SessionLocal, Base
from models import BaselineIdeal, BatchTanam

# ─── Raw data from user (nozzle 0.4mm, rockwool) ───
# Only odd days measured
PAPER_DAYS = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]

PAPER_TINGGI = [0, 1.2, 1.5, 2.0, 2.5, 3.5, 4.5, 5.5, 7.0, 9.0, 10.5, 14.5, 19.0, 24.0, 29.0]

# User dataset for leaf count
PAPER_DAUN = [0, 3, 4, 5, 6, 6, 7, 8, 9, 10, 12, 14, 16, 19, 23]


def interpolate_daily(days: list, values: list) -> dict:
    """Linearly interpolate between paper data points to fill all 29 days.
    
    Args:
        days: List of days with measured values (odd days).
        values: Corresponding measured values.
    
    Returns:
        Dictionary mapping day (1-29) to interpolated value.
    """
    result = {}
    
    # Create lookup from paper data
    day_to_val = dict(zip(days, values))
    
    for day in range(1, 30):
        if day in day_to_val:
            result[day] = day_to_val[day]
        else:
            # Find surrounding data points for interpolation
            lower_day = day - 1
            upper_day = day + 1
            
            # Walk to find actual data points
            while lower_day not in day_to_val and lower_day >= 1:
                lower_day -= 1
            while upper_day not in day_to_val and upper_day <= 29:
                upper_day += 1
            
            if lower_day in day_to_val and upper_day in day_to_val:
                # Linear interpolation
                fraction = (day - lower_day) / (upper_day - lower_day)
                val = day_to_val[lower_day] + fraction * (day_to_val[upper_day] - day_to_val[lower_day])
                result[day] = val
            elif lower_day in day_to_val:
                result[day] = day_to_val[lower_day]
            elif upper_day in day_to_val:
                result[day] = day_to_val[upper_day]
    
    return result


def seed_data():
    """Seed the database with baseline growth data and ensure tables exist."""
    # Ensure instance directory exists
    os.makedirs('instance', exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Clear existing baseline data to allow updating
        db.query(BaselineIdeal).delete()
        
        print("Seeding baseline data from user dataset...")
        
        # Interpolate to get all 29 days
        daily_tinggi = interpolate_daily(PAPER_DAYS, PAPER_TINGGI)
        daily_daun = interpolate_daily(PAPER_DAYS, PAPER_DAUN)
        
        for day in range(1, 30):
            baseline = BaselineIdeal(
                hari_ke=day,
                media_tanam='rockwool',
                ideal_tinggi=round(daily_tinggi[day], 1),
                ideal_daun=round(daily_daun[day])
            )
            db.add(baseline)
        
        db.commit()
        
        # Print summary table
        print("\n" + "=" * 50)
        print(f"{'Hari':>6} {'Tinggi (cm)':>12} {'Daun (helai)':>13}")
        print("-" * 50)
        for day in range(1, 30):
            marker = " *" if day in PAPER_DAYS else "  "
            print(f"{day:>6}{marker} {daily_tinggi[day]:>10.1f} {round(daily_daun[day]):>11}")
        print("-" * 50)
        print("* = data dari paper, lainnya interpolasi")
        print(f"\nTotal {db.query(BaselineIdeal).count()} baseline records created.")
        print("Seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    seed_data()
