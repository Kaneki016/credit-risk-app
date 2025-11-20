"""
Database setup script for Credit Risk App.
Creates database, tables, and initial data.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging

from dotenv import load_dotenv

from backend.database import check_connection, engine, init_db
from backend.database.models import Base

# Try to import psycopg2 (only needed for PostgreSQL)
try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


def create_database():
    """Create the database if it doesn't exist."""

    # Get database URL
    database_url = os.getenv("DATABASE_URL", "sqlite:///./credit_risk.db")

    print("=" * 70)
    print("Database Setup")
    print("=" * 70)
    print(f"\nDatabase URL: {database_url}")

    # Check if using SQLite
    if database_url.startswith("sqlite"):
        print("\n1. Using SQLite database")
        print("   ✅ SQLite requires no setup - database will be created automatically")
        return True

    # PostgreSQL setup
    db_name = os.getenv("DB_NAME", "credit_risk_db")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")

    print(f"\nDatabase: {db_name}")
    print(f"Host: {db_host}:{db_port}")
    print(f"User: {db_user}")

    # Check if psycopg2 is available
    if not HAS_PSYCOPG2:
        print("\n   ⚠️  psycopg2 not installed")
        print("   For PostgreSQL, install: pip install psycopg2-binary")
        print("   Or download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#psycopg")
        return False

    try:
        # Connect to PostgreSQL server (not to specific database)
        print("\n1. Connecting to PostgreSQL server...")
        conn = psycopg2.connect(dbname="postgres", user=db_user, password=db_password, host=db_host, port=db_port)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()

        if exists:
            print(f"   ✅ Database '{db_name}' already exists")
        else:
            # Create database
            print(f"   Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"   ✅ Database '{db_name}' created successfully")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"   ❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure PostgreSQL is installed and running")
        print("  2. Check your .env file has correct credentials")
        print("  3. Verify PostgreSQL is listening on the specified port")
        return False

    return True


def create_tables():
    """Create all tables in the database."""

    print("\n2. Creating database tables...")

    try:
        # Check connection
        if not check_connection():
            print("   ❌ Cannot connect to database")
            return False

        # Create all tables
        Base.metadata.create_all(bind=engine)

        # List created tables
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"   ✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"      • {table}")

        return True

    except Exception as e:
        print(f"   ❌ Error creating tables: {e}")
        return False


def verify_setup():
    """Verify database setup."""

    print("\n3. Verifying setup...")

    try:
        from sqlalchemy import inspect, text

        with engine.connect() as conn:
            # Test query
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

        # Count tables using inspector (works for both SQLite and PostgreSQL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        table_count = len(tables)

        print(f"   ✅ Database connection successful")
        print(f"   ✅ Found {table_count} tables")

        return True

    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False


def print_connection_string():
    """Print the connection string for reference."""

    db_name = os.getenv("DB_NAME", "credit_risk_db")
    db_user = os.getenv("DB_USER", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")

    print("\n" + "=" * 70)
    print("Connection Information")
    print("=" * 70)
    print(f"\nConnection String:")
    print(f"  postgresql://{db_user}:****@{db_host}:{db_port}/{db_name}")
    print(f"\nAdd to .env file:")
    print(f'  DATABASE_URL="postgresql://{db_user}:your_password@{db_host}:{db_port}/{db_name}"')


def main():
    """Main setup function."""

    print("\n🚀 Credit Risk App - Database Setup\n")

    # Step 1: Create database
    if not create_database():
        print("\n❌ Database creation failed")
        return 1

    # Step 2: Create tables
    if not create_tables():
        print("\n❌ Table creation failed")
        return 1

    # Step 3: Verify setup
    if not verify_setup():
        print("\n❌ Verification failed")
        return 1

    # Print connection info
    print_connection_string()

    # Success message
    print("\n" + "=" * 70)
    print("✅ Database Setup Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Start the API: python run.py")
    print("  2. Check database health: GET /db/health")
    print("  3. View statistics: GET /db/statistics")
    print("\nDatabase endpoints:")
    print("  • GET  /db/health - Check database connection")
    print("  • GET  /db/statistics - Get overall statistics")
    print("  • GET  /db/predictions - Get prediction history")
    print("  • GET  /db/predictions/{id} - Get prediction details")
    print("  • POST /db/predictions/{id}/feedback - Submit feedback")
    print("")

    return 0


if __name__ == "__main__":
    sys.exit(main())
