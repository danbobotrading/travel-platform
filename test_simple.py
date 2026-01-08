import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.session import AsyncSessionLocal

async def test_db():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT version();")
            version = result.scalar()
            print(f"✅ PostgreSQL connected: {version}")
            
            # Check if users table exists
            result = await session.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                );
            """)
            exists = result.scalar()
            print(f"✅ Users table exists: {exists}")
            
    except Exception as e:
        print(f"❌ Database error: {type(e).__name__}: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_db())
    sys.exit(0 if success else 1)
