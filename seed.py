import os
from app import app, db
from models import BaselineIdeal

def seed_data():
    with app.app_context():
        db.create_all()
        
        # Check if already seeded
        if BaselineIdeal.query.count() > 0:
            print("Database already seeded.")
            return

        print("Seeding baseline data...")
        # Dummy linear growth for Day 1 to 29
        # Height: Starts at 2cm, grows ~1cm per day.
        # Leaves: Starts at 2, adds ~1 leaf every 3 days.
        for day in range(1, 30):
            ideal_height = 2.0 + (day * 0.8)  # Dummy target
            ideal_leaves = 2 + (day // 3)     # Dummy target
            
            baseline = BaselineIdeal(
                hari_ke=day,
                ideal_tinggi=round(ideal_height, 1),
                ideal_daun=ideal_leaves
            )
            db.session.add(baseline)
        
        db.session.commit()
        print("Seeding completed successfully.")

if __name__ == '__main__':
    seed_data()
