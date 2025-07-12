import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Date, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True, nullable=False)
    type = Column(String)
    website_url = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    seeking_tags = Column(JSON, nullable=True)
    members = relationship("User", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    user_type = Column(String)
    profile_picture_url = Column(String, nullable=True)
    primary_goal = Column(String, nullable=True)
    about = Column(Text, nullable=True)
    looking_for = Column(JSON, nullable=True)
    
    # NEW FIELDS ADDED FOR FRONTEND COMPATIBILITY
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    experience = Column(JSON, nullable=True)  # Will store list of experience objects
    
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization", back_populates="members")

class Partnership(Base):
    __tablename__ = "partnerships"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_one_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    organization_two_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    agreement_type = Column(String, nullable=True)
    agreement_end_date = Column(Date, nullable=True)
    internal_manager_id = Column(String, ForeignKey("users.id"), nullable=True)
    external_contact_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization_one = relationship("Organization", foreign_keys=[organization_one_id])
    organization_two = relationship("Organization", foreign_keys=[organization_two_id])
    internal_manager = relationship("User", foreign_keys=[internal_manager_id])
    log_entries = relationship("PartnershipLogEntry", back_populates="partnership", cascade="all, delete-orphan")
    documents = relationship("PartnershipDocument", back_populates="partnership", cascade="all, delete-orphan")

class Target(Base):
    __tablename__ = "targets"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # UPDATED TARGET FIELDS TO MATCH FRONTEND EXPECTATIONS
    target_organization_name = Column(String, nullable=False)  # Changed from FK to simple string
    target_country = Column(String, nullable=True)
    target_type = Column(String, nullable=True)  # University, Agency, Institute
    partnership_type = Column(String, nullable=True)  # Student Recruitment, Joint Program, etc.
    
    priority = Column(String, nullable=False, default="Medium")  # High, Medium, Low
    stage = Column(String, nullable=False, default="Research")  # Research, Initial Contact, Discussion, Proposal, Negotiation
    next_action = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    contact_person = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_by_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization", foreign_keys=[organization_id])
    created_by = relationship("User", foreign_keys=[created_by_id])

class PartnershipLogEntry(Base):
    __tablename__ = "partnership_log_entries"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    partnership_id = Column(String, ForeignKey("partnerships.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=True)
    entry_type = Column(String, nullable=False)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    partnership = relationship("Partnership", back_populates="log_entries")

class PartnershipDocument(Base):
    __tablename__ = "partnership_documents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    partnership_id = Column(String, ForeignKey("partnerships.id"), nullable=False)
    uploaded_by_id = Column(String, ForeignKey("users.id"), nullable=True)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    partnership = relationship("Partnership", back_populates="documents")