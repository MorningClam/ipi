# fix_target_due_date.py
# Run this script to add the missing due_date column to targets table

from sqlalchemy import text, inspect
from database import engine

def fix_target_due_date():
    """
    Add the missing due_date column to the targets table
    """
    
    with engine.connect() as connection:
        # Check if due_date column exists
        inspector = inspect(engine)
        columns = inspector.get_columns('targets')
        column_names = [col['name'] for col in columns]
        
        print("Current targets table columns:")
        for col in column_names:
            print(f"  - {col}")
        
        if 'due_date' not in column_names:
            print("\n🔧 Adding missing due_date column...")
            try:
                # Add the due_date column
                connection.execute(text("""
                    ALTER TABLE targets 
                    ADD COLUMN due_date DATE
                """))
                connection.commit()
                print("✅ Successfully added due_date column to targets table!")
            except Exception as e:
                print(f"❌ Error adding due_date column: {e}")
        else:
            print("\n✅ due_date column already exists!")
        
        # Also check for other columns that might be missing
        expected_columns = [
            'id', 'organization_id', 'target_organization_name', 'target_country', 
            'target_type', 'partnership_type', 'priority', 'stage', 'next_action', 
            'due_date', 'contact_person', 'website_url', 'notes', 'created_by_id', 
            'created_at', 'updated_at'
        ]
        
        print("\n🔍 Checking for other missing columns...")
        missing_columns = []
        for expected_col in expected_columns:
            if expected_col not in column_names:
                missing_columns.append(expected_col)
        
        if missing_columns:
            print(f"⚠️  Missing columns found: {missing_columns}")
            print("You may need to run the full migration script to add these.")
        else:
            print("✅ All expected columns are present!")

if __name__ == "__main__":
    print("🚀 Fixing Target due_date Column")
    print("=" * 40)
    fix_target_due_date()
    print("\n🎯 Fix complete! Restart your FastAPI server.")