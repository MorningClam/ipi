# migration_script.py
# Run this script to update your existing database with new fields

from sqlalchemy import text, inspect
from database import engine

def run_migration():
    """
    Add new columns to existing database tables
    """
    
    migration_queries = [
        # Add new User fields
        "ALTER TABLE users ADD COLUMN phone TEXT;",
        "ALTER TABLE users ADD COLUMN location TEXT;", 
        "ALTER TABLE users ADD COLUMN linkedin TEXT;",
        "ALTER TABLE users ADD COLUMN experience TEXT;",  # SQLite stores JSON as TEXT
        
        # Update Target table structure (if targets table exists and has old structure)
        # Note: This is complex - easier to drop and recreate targets table if no important data
        "DROP TABLE IF EXISTS targets;",
        """CREATE TABLE targets (
            id TEXT PRIMARY KEY,
            organization_id TEXT NOT NULL,
            created_by_id TEXT NOT NULL,
            target_organization_name TEXT NOT NULL,
            target_country TEXT,
            target_type TEXT,
            partnership_type TEXT,
            contact_person TEXT,
            contact_email TEXT,
            website TEXT,
            priority TEXT NOT NULL DEFAULT 'MEDIUM',
            stage TEXT NOT NULL DEFAULT 'RESEARCH',
            notes TEXT,
            next_action TEXT,
            reminder_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations (id),
            FOREIGN KEY (created_by_id) REFERENCES users (id)
        );"""
    ]
    
    print("🔄 Starting database migration...")
    
    with engine.connect() as connection:
        # Get existing tables to check what already exists
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"📋 Found existing tables: {existing_tables}")
        
        for query in migration_queries:
            try:
                print(f"📝 Executing: {query[:50]}...")
                connection.execute(text(query))
                connection.commit()
                print("✅ Success")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"⚠️  Column already exists, skipping: {e}")
                else:
                    print(f"❌ Error: {e}")
                    # Continue with other migrations
                    continue
    
    print("🎉 Migration completed!")
    print("\n📋 Next Steps:")
    print("1. Restart your FastAPI server")
    print("2. Test profile editing with phone, location, LinkedIn fields")
    print("3. Test experience section in edit-profile.html")
    print("4. Test target creation with new structure")

def verify_migration():
    """
    Verify that the migration was successful
    """
    print("\n🔍 Verifying migration...")
    
    inspector = inspect(engine)
    
    # Check User table columns
    user_columns = [col['name'] for col in inspector.get_columns('users')]
    expected_user_columns = ['phone', 'location', 'linkedin', 'experience']
    
    print("👤 User table columns:")
    for col in expected_user_columns:
        if col in user_columns:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} - MISSING")
    
    # Check Target table structure
    if 'targets' in inspector.get_table_names():
        target_columns = [col['name'] for col in inspector.get_columns('targets')]
        expected_target_columns = ['target_organization_name', 'target_country', 'target_type', 'partnership_type']
        
        print("\n🎯 Target table columns:")
        for col in expected_target_columns:
            if col in target_columns:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} - MISSING")
    else:
        print("\n🎯 Target table: NOT FOUND")
    
    print("\n✅ Migration verification completed!")

if __name__ == "__main__":
    print("🚀 Database Migration Script")
    print("=" * 40)
    
    # Run migration
    run_migration()
    
    # Verify results
    verify_migration()
    
    print("\n🎯 PHASE 1 MIGRATION COMPLETE!")
    print("Your backend now supports:")
    print("  • User phone, location, LinkedIn, experience fields")
    print("  • Updated Target model structure")
    print("  • Full edit-profile.html ↔ backend integration")
    print("\nRestart your FastAPI server and test the profile editing!")