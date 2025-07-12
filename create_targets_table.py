#!/usr/bin/env python3
"""
Run this script to create the targets table in your database.
Run: python create_targets_table.py
"""

from database import engine
from models import Base, Target

def create_targets_table():
    """Create the targets table if it doesn't exist"""
    try:
        print("Creating targets table...")
        Target.__table__.create(engine, checkfirst=True)
        print("✅ Targets table created successfully!")
        print("You can now restart your FastAPI server and test 'Add to Targets'")
    except Exception as e:
        print(f"❌ Error creating targets table: {e}")
        print("Make sure your database is accessible and models.py is correct")

if __name__ == "__main__":
    create_targets_table()