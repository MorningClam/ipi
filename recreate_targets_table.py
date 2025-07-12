# recreate_targets_table.py
# Run this to completely recreate the targets table with correct structure

from sqlalchemy import text
from database import engine

def recreate_targets_table():
    """
    Drop and recreate the targets table with the correct structure
    """
    
    with engine.connect() as connection:
        try:
            print("🗑️  Dropping existing targets table...")
            connection.execute(text("DROP TABLE IF EXISTS targets"))
            
            print("🔧 Creating new targets table with correct structure...")
            connection.execute(text("""
                CREATE TABLE targets (
                    id TEXT PRIMARY KEY,
                    organization_id TEXT NOT NULL,
                    target_organization_name TEXT NOT NULL,
                    target_country TEXT,
                    target_type TEXT,
                    partnership_type TEXT,
                    priority TEXT NOT NULL DEFAULT 'MEDIUM',
                    stage TEXT NOT NULL DEFAULT 'RESEARCH',
                    next_action TEXT,
                    due_date DATE,
                    contact_person TEXT,
                    website_url TEXT,
                    notes TEXT,
                    created_by_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations (id),
                    FOREIGN KEY (created_by_id) REFERENCES users (id)
                )
            """))
            
            connection.commit()
            print("✅ Successfully recreated targets table!")
            print("🚀 Restart your FastAPI server now.")
            
        except Exception as e:
            print(f"❌ Error recreating targets table: {e}")
            connection.rollback()

if __name__ == "__main__":
    print("🚀 Recreating Targets Table")
    print("=" * 40)
    recreate_targets_table()