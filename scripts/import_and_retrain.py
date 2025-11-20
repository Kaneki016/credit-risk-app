#!/usr/bin/env python3
"""
Import CSV Dataset and Retrain Model
Imports credit_risk_dataset.csv into database and triggers model retraining.
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging

from sqlalchemy import text

from backend.database.config import SessionLocal, check_connection, init_db
from backend.database.models import LoanApplication, Prediction
from backend.services.database_retraining import DatabaseRetrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_dataset():
    """Find the credit risk dataset CSV file."""
    possible_paths = [
        "data/credit_risk_dataset.csv",
        "credit_risk_dataset.csv",
        "../data/credit_risk_dataset.csv",
    ]

    for path in possible_paths:
        if Path(path).exists():
            logger.info(f"Found dataset at: {path}")
            return path

    logger.error("Dataset not found. Checked locations:")
    for path in possible_paths:
        logger.error(f"  - {path}")
    return None


def load_dataset(csv_path):
    """Load and validate the dataset."""
    logger.info(f"Loading dataset from {csv_path}...")

    try:
        df = pd.read_csv(csv_path)
        logger.info(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")

        # Show column names
        logger.info(f"Columns: {', '.join(df.columns.tolist())}")

        # Check for required columns
        required_cols = ["loan_status"]  # Target variable
        missing = [col for col in required_cols if col not in df.columns]

        if missing:
            logger.error(f"Missing required columns: {missing}")
            return None

        return df

    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        return None


def import_to_database(df, db):
    """Import dataset into database as predictions with actual outcomes."""
    logger.info("\n" + "=" * 70)
    logger.info("IMPORTING DATA TO DATABASE")
    logger.info("=" * 70)

    # Map column names (handle different naming conventions)
    column_mapping = {
        "person_age": "person_age",
        "person_income": "person_income",
        "person_emp_length": "person_emp_length",
        "person_home_ownership": "home_ownership",
        "loan_amnt": "loan_amnt",
        "loan_intent": "loan_intent",
        "loan_grade": "loan_grade",
        "loan_int_rate": "loan_int_rate",
        "loan_percent_income": "loan_percent_income",
        "cb_person_default_on_file": "default_on_file",
        "cb_person_cred_hist_length": "cb_person_cred_hist_length",
        "loan_status": "loan_status",
    }

    imported_count = 0
    error_count = 0

    logger.info(f"Processing {len(df)} rows...")

    for idx, row in df.iterrows():
        try:
            # Extract input features
            input_features = {}
            for csv_col, db_col in column_mapping.items():
                if csv_col in df.columns and csv_col != "loan_status":
                    value = row[csv_col]
                    # Handle NaN values
                    if pd.notna(value):
                        input_features[db_col] = value

            # Get actual outcome (loan_status)
            actual_outcome = int(row["loan_status"]) if pd.notna(row["loan_status"]) else None

            # Create a "prediction" record with actual outcome
            # This simulates predictions that we know the actual results for
            prediction = Prediction(
                input_features=input_features,
                risk_level="Unknown",  # Will be updated during retraining
                probability_default=0.5,  # Placeholder
                binary_prediction=actual_outcome if actual_outcome is not None else 0,
                model_type="imported_data",
                actual_outcome=actual_outcome,
                created_at=datetime.now(),
            )

            db.add(prediction)
            imported_count += 1

            # Commit in batches for better performance
            if imported_count % 100 == 0:
                db.commit()
                logger.info(f"  Imported {imported_count} rows...")

        except Exception as e:
            error_count += 1
            if error_count <= 5:  # Show first 5 errors
                logger.warning(f"  Error importing row {idx}: {e}")

    # Final commit
    db.commit()

    logger.info(f"\n✅ Import complete:")
    logger.info(f"   Successfully imported: {imported_count} rows")
    if error_count > 0:
        logger.warning(f"   Errors: {error_count} rows")

    return imported_count


def retrain_model(db):
    """Retrain the model using database data."""
    logger.info("\n" + "=" * 70)
    logger.info("RETRAINING MODEL")
    logger.info("=" * 70)

    try:
        retrainer = DatabaseRetrainer(
            min_samples=100,  # Minimum samples needed
            min_feedback_ratio=0.01,  # At least 1% should have feedback (lowered for imported data)
        )

        # Check if we have enough data
        logger.info("\nChecking retraining readiness...")
        readiness = retrainer.check_retraining_readiness(db)

        logger.info(f"  Total predictions: {readiness['total_predictions']}")
        logger.info(f"  With feedback: {readiness['feedback_count']}")
        logger.info(f"  Feedback ratio: {readiness['feedback_ratio']:.1%}")
        logger.info(f"  Ready to retrain: {readiness['is_ready']}")

        if not readiness["is_ready"]:
            logger.warning("\n⚠️  Not enough data for retraining")
            logger.warning(f"   Need at least {retrainer.min_samples} samples")
            logger.warning(f"   Need at least {retrainer.min_feedback_ratio:.0%} feedback ratio")
            return None

        # Retrain the model
        logger.info("\n🔄 Starting model retraining...")
        result = retrainer.retrain_model(db=db, test_size=0.2, save_model=True)

        logger.info("\n✅ Retraining complete!")
        logger.info(f"   Training samples: {result['training_samples']}")
        logger.info(f"   Test samples: {result['test_samples']}")
        logger.info(f"   Test Accuracy: {result['metrics']['accuracy']:.2%}")
        logger.info(f"   Test AUC: {result['metrics']['auc_roc']:.4f}")
        logger.info(f"   Model saved: {result.get('model_version') is not None}")

        if result.get("model_version"):
            logger.info(f"   Model version: {result['model_version']}")

        return result

    except Exception as e:
        logger.error(f"\n❌ Retraining failed: {e}")
        import traceback

        traceback.print_exc()
        return None


def show_summary(db):
    """Show summary of database contents."""
    logger.info("\n" + "=" * 70)
    logger.info("DATABASE SUMMARY")
    logger.info("=" * 70)

    try:
        total_predictions = db.query(Prediction).count()
        with_feedback = db.query(Prediction).filter(Prediction.actual_outcome.isnot(None)).count()

        logger.info(f"\nTotal predictions: {total_predictions}")
        logger.info(f"With feedback: {with_feedback} ({with_feedback/total_predictions*100:.1f}%)")

        # Count by model type
        model_types = db.execute(
            text(
                """
            SELECT model_type, COUNT(*) as count
            FROM predictions
            GROUP BY model_type
            ORDER BY count DESC
        """
            )
        ).fetchall()

        logger.info("\nBy model type:")
        for model_type, count in model_types:
            logger.info(f"  {model_type}: {count}")

        # Count by actual outcome
        if with_feedback > 0:
            outcomes = db.execute(
                text(
                    """
                SELECT actual_outcome, COUNT(*) as count
                FROM predictions
                WHERE actual_outcome IS NOT NULL
                GROUP BY actual_outcome
            """
                )
            ).fetchall()

            logger.info("\nActual outcomes:")
            for outcome, count in outcomes:
                outcome_label = "Default" if outcome == 1 else "No Default"
                logger.info(f"  {outcome_label}: {count} ({count/with_feedback*100:.1f}%)")

    except Exception as e:
        logger.error(f"Error generating summary: {e}")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Import CSV dataset and retrain model")
    parser.add_argument("--csv", help="Path to CSV file (default: auto-detect)", default=None)
    parser.add_argument("--skip-import", action="store_true", help="Skip import, only retrain with existing data")
    parser.add_argument("--skip-retrain", action="store_true", help="Only import data, skip retraining")
    parser.add_argument("--clear-first", action="store_true", help="Clear existing predictions before import")

    args = parser.parse_args()

    # Print header
    print("\n" + "=" * 70)
    print("  IMPORT CSV DATASET AND RETRAIN MODEL")
    print("=" * 70)

    # Check database connection
    logger.info("\nChecking database connection...")
    if not check_connection():
        logger.error("❌ Cannot connect to database")
        sys.exit(1)

    logger.info("✅ Database connected")

    # Initialize database (create tables if needed)
    init_db()

    # Get database session
    db = SessionLocal()

    try:
        # Clear existing data if requested
        if args.clear_first:
            logger.info("\n🗑️  Clearing existing predictions...")
            deleted = db.query(Prediction).delete()
            db.commit()
            logger.info(f"   Deleted {deleted} existing predictions")

        # Import data
        if not args.skip_import:
            # Find dataset
            csv_path = args.csv if args.csv else find_dataset()

            if not csv_path:
                logger.error("\n❌ Dataset not found")
                logger.info("\nUsage:")
                logger.info("  python scripts/import_and_retrain.py --csv path/to/dataset.csv")
                sys.exit(1)

            # Load dataset
            df = load_dataset(csv_path)
            if df is None:
                sys.exit(1)

            # Import to database
            imported = import_to_database(df, db)

            if imported == 0:
                logger.error("❌ No data imported")
                sys.exit(1)
        else:
            logger.info("\n⏭️  Skipping import (--skip-import flag)")

        # Show summary
        show_summary(db)

        # Retrain model
        if not args.skip_retrain:
            result = retrain_model(db)

            if result:
                logger.info("\n" + "=" * 70)
                logger.info("✅ SUCCESS - Model retrained with imported data!")
                logger.info("=" * 70)
                logger.info("\nNext steps:")
                logger.info("  1. Restart the API: python run.py")
                logger.info("  2. Or reload model: curl -X POST http://localhost:8000/reload_model")
                logger.info("  3. Test predictions with new model")
            else:
                logger.warning("\n⚠️  Import successful but retraining failed")
                logger.info("   You can try retraining later with:")
                logger.info("   python scripts/import_and_retrain.py --skip-import")
        else:
            logger.info("\n⏭️  Skipping retraining (--skip-retrain flag)")
            logger.info("\nTo retrain later, run:")
            logger.info("  python scripts/import_and_retrain.py --skip-import")

    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
