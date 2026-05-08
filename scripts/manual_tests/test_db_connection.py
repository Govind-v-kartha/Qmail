"""
Test Railway PostgreSQL Database Connection
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        return False
    
    print("=" * 60)
    print("Testing Railway PostgreSQL Connection")
    print("=" * 60)
    print(f"\n📍 Database URL: {database_url[:30]}...{database_url[-20:]}")
    
    try:
        # Create engine
        print("\n⏳ Connecting to database...")
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as connection:
            # Get PostgreSQL version
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            
            # Get database name
            result = connection.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            
            # Get current user
            result = connection.execute(text("SELECT current_user;"))
            db_user = result.fetchone()[0]
            
            # Count tables
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """))
            table_count = result.fetchone()[0]
            
            print("\n✅ CONNECTION SUCCESSFUL!")
            print("\n" + "=" * 60)
            print("Database Information:")
            print("=" * 60)
            print(f"📊 Database: {db_name}")
            print(f"👤 User: {db_user}")
            print(f"📋 Tables: {table_count}")
            print(f"🔧 PostgreSQL Version: {version.split(',')[0]}")
            print("=" * 60)
            
            if table_count == 0:
                print("\n⚠️  WARNING: No tables found!")
                print("   Run: python recreate_database.py")
            else:
                # List tables
                result = connection.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """))
                tables = [row[0] for row in result]
                print(f"\n📋 Tables in database:")
                for table in tables:
                    print(f"   • {table}")
            
            return True
            
    except OperationalError as e:
        print("\n❌ CONNECTION FAILED!")
        print(f"\nError: {str(e)}")
        print("\nPossible issues:")
        print("  1. Wrong DATABASE_URL in .env file")
        print("  2. Railway database is down")
        print("  3. Network/firewall blocking connection")
        print("  4. Missing psycopg2-binary package")
        return False
    
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_connection()
    exit(0 if success else 1)
