import asyncio
import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

async def test_database():
    print("?? COMPREHENSIVE DATABASE TEST")
    print("=" * 50)
    
    try:
        # Test 1: Import settings
        from core.config.settings import settings
        print(f"? Settings loaded: {settings.DATABASE_URL}")
        
        # Test 2: Import models
        from database.base import Base
        from database.models.user import User
        print(f"? Models imported: {User.__tablename__}")
        
        # Test 3: Create engine and connect - CONVERT TO STRING
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        engine = create_async_engine(str(settings.DATABASE_URL))
        
        print("\n?? Testing database connection...")
        async with engine.connect() as conn:
            # Test PostgreSQL version - USE text() for SQL expressions
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"? PostgreSQL: {version.split(',')[0]}")
            
            # Test if users table exists
            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
            )
            table_exists = result.scalar()
            print(f"? Users table exists: {table_exists}")
            
            # Test table structure
            if table_exists:
                result = await conn.execute(
                    text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position")
                )
                columns = result.fetchall()
                print(f"? Table columns: {len(columns)}")
                for col in columns[:5]:  # Show first 5 columns
                    print(f"   - {col[0]}: {col[1]}")
                if len(columns) > 5:
                    print(f"   ... and {len(columns) - 5} more columns")
        
        await engine.dispose()
        
        # Test 4: Test session factory
        print("\n??? Testing session factory...")
        from database.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            print("? Session factory works")
        
        print("\n" + "=" * 50)
        print("?? ALL DATABASE TESTS PASSED!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n? Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_database())
    sys.exit(0 if success else 1)
