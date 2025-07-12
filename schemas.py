from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class UserSummary(BaseModel):
    id: str
    full_name: str
    model_config = ConfigDict(from_attributes=True)

class OrganizationSummary(BaseModel):
    id: str
    name: str
    model_config = ConfigDict(from_attributes=True)

class OrganizationCreate(BaseModel):
    name: str
    organization_type: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: str
    name: str
    organization_type: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class TargetCreate(BaseModel):
    target_organization_name: str
    target_country: Optional[str] = None
    target_type: Optional[str] = None
    partnership_type: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    priority: str = "MEDIUM"
    stage: str = "RESEARCH"
    notes: Optional[str] = None
    next_action: Optional[str] = None
    reminder_date: Optional[date] = None

class TargetUpdate(BaseModel):
    target_organization_name: Optional[str] = None
    target_country: Optional[str] = None
    target_type: Optional[str] = None
    partnership_type: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    priority: Optional[str] = None
    stage: Optional[str] = None
    notes: Optional[str] = None
    next_action: Optional[str] = None
    reminder_date: Optional[date] = None

class TargetResponse(BaseModel):
    id: str
    organization_id: str
    created_by_id: str
    target_organization_name: str
    target_country: Optional[str] = None
    target_type: Optional[str] = None
    partnership_type: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    priority: str
    stage: str
    notes: Optional[str] = None
    next_action: Optional[str] = None
    reminder_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UserSummary] = None
    model_config = ConfigDict(from_attributes=True)

class PartnershipCreate(BaseModel):
    organization_two_id: str
    agreement_type: Optional[str] = None
    agreement_end_date: Optional[date] = None

class PartnershipSummary(BaseModel):
    id: str
    organization_one_id: str
    organization_two_id: str
    status: str
    agreement_type: Optional[str] = None
    agreement_end_date: Optional[date] = None
    created_at: datetime
    organization_one: Optional[OrganizationSummary] = None
    organization_two: Optional[OrganizationSummary] = None
    model_config = ConfigDict(from_attributes=True)

# NEW PARTNERSHIP WORKFLOW SCHEMAS
class PartnershipStatusUpdate(BaseModel):
    status: str  # PENDING, ACTIVE, DECLINED, EXPIRED
    notes: Optional[str] = None

class PartnershipLogEntryCreate(BaseModel):
    entry_type: str  # UPDATE, NOTE, DOCUMENT, STATUS_CHANGE
    title: str
    description: Optional[str] = None

class PartnershipLogEntryResponse(BaseModel):
    id: str
    partnership_id: str
    entry_type: str
    title: str
    description: Optional[str] = None
    created_by_id: str
    created_at: datetime
    created_by: Optional[UserSummary] = None
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    user_type: Optional[str] = None
    email: Optional[str] = None  # Added email updates
    organization_id: Optional[str] = None
    profile_picture_url: Optional[str] = None
    primary_goal: Optional[str] = None
    about: Optional[str] = None
    looking_for: Optional[List[str]] = None
    # NEW FIELDS ADDED FOR PHASE 1
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    experience: Optional[List[Dict[str, Any]]] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    user_type: Optional[str] = None
    profile_picture_url: Optional[str] = None
    organization_id: Optional[str] = None
    primary_goal: Optional[str] = None
    about: Optional[str] = None
    looking_for: Optional[List[str]] = None
    # NEW FIELDS ADDED FOR PHASE 1
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    experience: Optional[List[Dict[str, Any]]] = None
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str