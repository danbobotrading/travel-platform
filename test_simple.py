import asyncio
import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

async def test():
    print("?? Testing database setup...")
    
    try:
        # Test 1: Import settings - use correct path
        from core.config.settings import settings
        print(f"? Settings loaded: {settings.DATABASE_URL}")
        print(f"? App name: {settings.APP_NAME}")
        
        # Test 2: Import Base
        from database.base import Base
        print("? Base imported")
        
        # Test 3: Import model
        from database.models.user import User
        print("? User model imported")
        
        # Test 4: Check table metadata
        print(f"? User table: {User.__tablename__}")
        
        print("\n?? Basic imports work!")
        return True
        
    except Exception as e:
        print(f"\n? Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
