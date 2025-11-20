#!/usr/bin/env python3
"""
Database Inspection Script
Displays contents and statistics of the credit risk database.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime

import pandas as pd
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from backend.database import crud
from backend.database.config import DATABASE_URL, SessionLocal, check_connection, engine
from backend.database.models import AuditLog, FeatureEngineering, LoanApplication, MitigationPlan, ModelMetrics, Prediction


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{title}")
    print("-" * 70)


def check_database_exists():
    """Check if database exists and is accessible."""
    print_header("DATABASE CONNECTION")
    print(f"Database URL: {DATABASE_URL}")

    if check_connection():
        print("✅ Database connection successful")
        return True
    else:
        print("❌ Database connection failed")
        return False


def list_tables():
    """List all tables in the database."""
    print_section("TABLES")

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if not tables:
        print("No tables found in database")
        return []

    print(f"Found {len(tables)} tables:")
    for i, table in enumerate(tables, 1):
        print(f"  {i}. {table}")

    return tables


def get_table_info(table_name):
    """Get detailed information about a table."""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)

    print(f"\nTable: {table_name}")
    print(f"Columns ({len(columns)}):")
    for col in columns:
        nullable = "NULL" if col["nullable"] else "NOT NULL"
        print(f"  - {col['name']}: {col['type']} {nullable}")


def count_records():
    """Count records in each table."""
    print_section("RECORD COUNTS")

    db = SessionLocal()
    try:
        counts = {
            "loan_applications": db.query(LoanApplication).count(),
            "predictions": db.query(Prediction).count(),
            "feature_engineering": db.query(FeatureEngineering).count(),
            "mitigation_plans": db.query(MitigationPlan).count(),
            "audit_logs": db.query(AuditLog).count(),
            "model_metrics": db.query(ModelMetrics).count(),
        }

        total = sum(counts.values())
        print(f"Total records across all tables: {total}")
        print()

        for table, count in counts.items():
            print(f"  {table:.<40} {count:>6} records")

        return counts
    except Exception as e:
        print(f"Error counting records: {e}")
        return {}
    finally:
        db.close()


def show_recent_predictions(limit=10):
    """Show recent predictions."""
    print_section(f"RECENT PREDICTIONS (Last {limit})")

    db = SessionLocal()
    try:
        predictions = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(limit).all()

        if not predictions:
            print("No predictions found")
            return

        print(f"\nFound {len(predictions)} recent predictions:\n")

        for i, pred in enumerate(predictions, 1):
            print(f"{i}. ID: {pred.id}")
            print(f"   Risk Level: {pred.risk_level}")
            print(f"   Probability: {pred.probability_default:.2%}")
            print(f"   Model Type: {pred.model_type}")
            print(f"   Created: {pred.created_at}")
            if pred.actual_outcome is not None:
                print(f"   Actual Outcome: {pred.actual_outcome}")
            print()

    except Exception as e:
        print(f"Error fetching predictions: {e}")
    finally:
        db.close()


def show_statistics():
    """Show database statistics."""
    print_section("STATISTICS")

    db = SessionLocal()
    try:
        # Prediction statistics
        total_predictions = db.query(Prediction).count()

        if total_predictions == 0:
            print("No predictions in database yet")
            return

        # Count by risk level
        print("\nPredictions by Risk Level:")
        risk_levels = db.execute(
            text(
                """
            SELECT risk_level, COUNT(*) as count
            FROM predictions
            GROUP BY risk_level
            ORDER BY count DESC
        """
            )
        ).fetchall()

        for risk_level, count in risk_levels:
            percentage = (count / total_predictions) * 100
            print(f"  {risk_level:.<40} {count:>6} ({percentage:>5.1f}%)")

        # Count by model type
        print("\nPredictions by Model Type:")
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

        for model_type, count in model_types:
            percentage = (count / total_predictions) * 100
            print(f"  {model_type:.<40} {count:>6} ({percentage:>5.1f}%)")

        # Predictions with feedback
        with_feedback = db.query(Prediction).filter(Prediction.actual_outcome.isnot(None)).count()

        print(f"\nPredictions with Feedback:")
        print(f"  Total: {with_feedback} ({(with_feedback/total_predictions)*100:.1f}%)")

        # Calculate accuracy if we have feedback
        if with_feedback > 0:
            correct = db.execute(
                text(
                    """
                SELECT COUNT(*) as count
                FROM predictions
                WHERE actual_outcome IS NOT NULL
                AND binary_prediction = actual_outcome
            """
                )
            ).fetchone()[0]

            accuracy = (correct / with_feedback) * 100
            print(f"  Accuracy: {accuracy:.1f}% ({correct}/{with_feedback})")

    except Exception as e:
        print(f"Error calculating statistics: {e}")
    finally:
        db.close()


def export_to_csv(table_name, output_file=None):
    """Export table to CSV."""
    if output_file is None:
        output_file = f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, engine)
        df.to_csv(output_file, index=False)
        print(f"✅ Exported {len(df)} rows to {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Error exporting {table_name}: {e}")
        return None


def show_sample_data(table_name, limit=5):
    """Show sample data from a table."""
    print_section(f"SAMPLE DATA: {table_name} (First {limit} rows)")

    try:
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df = pd.read_sql(query, engine)

        if df.empty:
            print(f"No data in {table_name}")
            return

        # Display with pandas formatting
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", None)
        pd.set_option("display.max_colwidth", 50)

        print(df.to_string())

    except Exception as e:
        print(f"Error fetching sample data: {e}")


def interactive_menu():
    """Interactive menu for database inspection."""
    while True:
        print_header("DATABASE INSPECTOR - MENU")
        print("\n1. Show table list")
        print("2. Show record counts")
        print("3. Show recent predictions")
        print("4. Show statistics")
        print("5. Show sample data from table")
        print("6. Export table to CSV")
        print("7. Show table structure")
        print("8. Run full inspection")
        print("9. Exit")

        choice = input("\nEnter your choice (1-9): ").strip()

        if choice == "1":
            list_tables()
        elif choice == "2":
            count_records()
        elif choice == "3":
            limit = input("How many predictions to show? (default 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            show_recent_predictions(limit)
        elif choice == "4":
            show_statistics()
        elif choice == "5":
            table = input("Enter table name: ").strip()
            limit = input("How many rows? (default 5): ").strip()
            limit = int(limit) if limit.isdigit() else 5
            show_sample_data(table, limit)
        elif choice == "6":
            table = input("Enter table name: ").strip()
            output = input("Output file (press Enter for auto): ").strip()
            export_to_csv(table, output if output else None)
        elif choice == "7":
            table = input("Enter table name: ").strip()
            get_table_info(table)
        elif choice == "8":
            run_full_inspection()
        elif choice == "9":
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

        input("\nPress Enter to continue...")


def run_full_inspection():
    """Run a complete database inspection."""
    print_header("FULL DATABASE INSPECTION")

    # Check connection
    if not check_database_exists():
        return

    # List tables
    tables = list_tables()

    if not tables:
        print("\n⚠️  Database is empty. No tables found.")
        return

    # Count records
    counts = count_records()

    # Show statistics if we have predictions
    if counts.get("predictions", 0) > 0:
        show_statistics()
        show_recent_predictions(5)
    else:
        print("\n⚠️  No predictions in database yet.")

    print_header("INSPECTION COMPLETE")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Inspect Credit Risk Database")
    parser.add_argument("--full", action="store_true", help="Run full inspection")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--export", metavar="TABLE", help="Export table to CSV")
    parser.add_argument("--sample", metavar="TABLE", help="Show sample data from table")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")

    args = parser.parse_args()

    # Check connection first
    if not check_database_exists():
        print("\n❌ Cannot connect to database. Please check your configuration.")
        sys.exit(1)

    if args.interactive:
        interactive_menu()
    elif args.full:
        run_full_inspection()
    elif args.export:
        export_to_csv(args.export)
    elif args.sample:
        show_sample_data(args.sample)
    elif args.stats:
        show_statistics()
    else:
        # Default: run full inspection
        run_full_inspection()


if __name__ == "__main__":
    main()
