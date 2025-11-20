#!/usr/bin/env python3
"""
Quick Database Check
Simple script to quickly check database contents.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from backend.database.config import DATABASE_URL, SessionLocal, check_connection
from backend.database.models import LoanApplication, Prediction


def main():
    print("=" * 60)
    print("  QUICK DATABASE CHECK")
    print("=" * 60)

    print(f"\n📍 Database: {DATABASE_URL}")

    # Check connection
    if not check_connection():
        print("❌ Cannot connect to database")
        return

    print("✅ Database connected")

    # Get counts
    db = SessionLocal()
    try:
        pred_count = db.query(Prediction).count()
        app_count = db.query(LoanApplication).count()

        print(f"\n📊 Record Counts:")
        print(f"   Predictions: {pred_count}")
        print(f"   Applications: {app_count}")

        if pred_count > 0:
            # Show recent predictions
            recent = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(5).all()

            print(f"\n🔍 Last 5 Predictions:")
            for i, pred in enumerate(recent, 1):
                print(f"   {i}. {pred.risk_level} - {pred.probability_default:.1%} - {pred.created_at}")

            # Show statistics
            high_risk = db.query(Prediction).filter(Prediction.risk_level.like("%High%")).count()
            low_risk = db.query(Prediction).filter(Prediction.risk_level.like("%Low%")).count()

            print(f"\n📈 Risk Distribution:")
            print(f"   High Risk: {high_risk} ({high_risk/pred_count*100:.1f}%)")
            print(f"   Low Risk: {low_risk} ({low_risk/pred_count*100:.1f}%)")

            # Check for feedback
            with_feedback = db.query(Prediction).filter(Prediction.actual_outcome.isnot(None)).count()

            if with_feedback > 0:
                print(f"\n💬 Feedback: {with_feedback} predictions have actual outcomes")
        else:
            print("\n⚠️  No predictions in database yet")
            print("   Make some predictions to see data here!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("For detailed inspection, run: python scripts/inspect_database.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
