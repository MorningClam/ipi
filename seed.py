import uuid
from datetime import datetime, date
from database import SessionLocal, Base, engine
from models import User, Organization, Partnership
from security import get_password_hash  # Import the proper hash function

# Create database tables
Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    
    try:
        print("--- Deleting old data... ---")
        # Delete existing data in correct order (partnerships first due to foreign keys)
        db.query(Partnership).delete()
        db.query(User).delete()
        db.query(Organization).delete()
        db.commit()
        
        print("--- Creating new test data... ---")
        
        # Create organizations first
        org1 = Organization(
            id=str(uuid.uuid4()),
            name="Proposer University",
            type="University",
            website_url="https://proposer-university.edu",
            logo_url="https://via.placeholder.com/100x100?text=PU",
            location="United States",
            description="A leading research university focused on international education.",
            seeking_tags=["student_exchange", "research_collaboration"]
        )
        
        org2 = Organization(
            id=str(uuid.uuid4()),
            name="Recipient Agency", 
            type="Education Agency",
            website_url="https://recipient-agency.ca",
            logo_url="https://via.placeholder.com/100x100?text=RA",
            location="Canada",
            description="Government agency promoting international student exchange.",
            seeking_tags=["partnerships", "student_programs"]
        )
        
        db.add_all([org1, org2])
        db.commit()
        
        # Create users with properly hashed passwords
        user1 = User(
            id=str(uuid.uuid4()),
            email="proposer@example.com",
            full_name="John Proposer",
            hashed_password=get_password_hash("password123"),  # Use proper hashing
            user_type="admin",
            profile_picture_url="https://via.placeholder.com/150x150?text=JP",
            organization_id=org1.id
        )
        
        user2 = User(
            id=str(uuid.uuid4()),
            email="recipient@example.com",
            full_name="Jane Recipient",
            hashed_password=get_password_hash("password456"),  # Use proper hashing
            user_type="admin",
            profile_picture_url="https://via.placeholder.com/150x150?text=JR",
            organization_id=org2.id
        )
        
        db.add_all([user1, user2])
        db.commit()
        
        # Create a partnership
        partnership = Partnership(
            id=str(uuid.uuid4()),
            organization_one_id=org1.id,
            organization_two_id=org2.id,
            status="PENDING",
            agreement_type="Student Exchange",
            created_at=datetime.now()
        )
        
        db.add(partnership)
        db.commit()
        
        print("--- Database has been seeded successfully! ---")
        print("--- The following test users and organizations have been created: ---")
        print(f"User A: {user1.email} (password: password123)")
        print(f"User B: {user2.email} (password: password456)")
        print(f"A PENDING partnership now exists between '{org1.name}' and '{org2.name}'.")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()