from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated, List
from datetime import timedelta, datetime
import uuid

import models, schemas, security
from database import SessionLocal, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get current user
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        from jose import jwt, JWTError
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# --- AUTHENTICATION ENDPOINTS ---

@app.post("/api/auth/register", tags=["Authentication"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = security.create_user(db=db, user=user)
    
    # Return simple dict instead of SQLAlchemy object
    return {
        "id": created_user.id,
        "email": created_user.email,
        "full_name": created_user.full_name,
        "user_type": getattr(created_user, 'user_type', None),
        "organization_id": getattr(created_user, 'organization_id', None)
    }

@app.post("/api/auth/login", tags=["Authentication"])
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- USER ENDPOINTS ---

@app.get("/api/users/me", tags=["Users"])
def read_users_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    # Return simple dict instead of SQLAlchemy object
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "user_type": getattr(current_user, 'user_type', None),
        "profile_picture_url": getattr(current_user, 'profile_picture_url', None),
        "organization_id": getattr(current_user, 'organization_id', None),
        "primary_goal": getattr(current_user, 'primary_goal', None),
        "about": getattr(current_user, 'about', None),
        "looking_for": getattr(current_user, 'looking_for', None),
        "phone": getattr(current_user, 'phone', None),
        "location": getattr(current_user, 'location', None),
        "linkedin": getattr(current_user, 'linkedin', None),
        "experience": getattr(current_user, 'experience', None)
    }

@app.put("/api/users/me", tags=["Users"])
def update_user_profile(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Update user fields - INCLUDING NEW FIELDS FROM PHASE 1
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.user_type is not None:
        current_user.user_type = user_update.user_type
    if user_update.email is not None:
        # Check if email is already taken by another user
        existing_user = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_update.email
    if user_update.organization_id is not None:
        current_user.organization_id = user_update.organization_id
    if user_update.profile_picture_url is not None:
        current_user.profile_picture_url = user_update.profile_picture_url
    if user_update.primary_goal is not None:
        current_user.primary_goal = user_update.primary_goal
    if user_update.about is not None:
        current_user.about = user_update.about
    if user_update.looking_for is not None:
        current_user.looking_for = user_update.looking_for
    # NEW FIELDS FROM PHASE 1
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    if user_update.location is not None:
        current_user.location = user_update.location
    if user_update.linkedin is not None:
        current_user.linkedin = user_update.linkedin
    if user_update.experience is not None:
        current_user.experience = user_update.experience
    
    db.commit()
    db.refresh(current_user)
    
    # Return simple dict instead of SQLAlchemy object
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "user_type": getattr(current_user, 'user_type', None),
        "profile_picture_url": getattr(current_user, 'profile_picture_url', None),
        "organization_id": getattr(current_user, 'organization_id', None),
        "primary_goal": getattr(current_user, 'primary_goal', None),
        "about": getattr(current_user, 'about', None),
        "looking_for": getattr(current_user, 'looking_for', None),
        "phone": getattr(current_user, 'phone', None),
        "location": getattr(current_user, 'location', None),
        "linkedin": getattr(current_user, 'linkedin', None),
        "experience": getattr(current_user, 'experience', None)
    }

# --- ORGANIZATIONS ENDPOINTS ---

@app.get("/api/organizations", tags=["Organizations"])
def get_all_organizations(db: Session = Depends(get_db)):
    organizations = db.query(models.Organization).all()
    # Return as simple dictionaries to avoid validation errors
    return [
        {
            "id": org.id,
            "name": org.name,
            "type": getattr(org, 'type', None),
            "website_url": getattr(org, 'website_url', None),
            "logo_url": getattr(org, 'logo_url', None),
            "location": getattr(org, 'location', None),
            "description": getattr(org, 'description', None),
            "seeking_tags": getattr(org, 'seeking_tags', None)
        }
        for org in organizations
    ]

@app.post("/api/organizations", tags=["Organizations"])
def create_organization(
    org: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_org = models.Organization(
        id=str(uuid.uuid4()),
        **org.model_dump()
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    # Return as simple dictionary to avoid validation errors
    return {
        "id": new_org.id,
        "name": new_org.name,
        "type": getattr(new_org, 'type', None),
        "website_url": getattr(new_org, 'website_url', None),
        "logo_url": getattr(new_org, 'logo_url', None),
        "location": getattr(new_org, 'location', None),
        "description": getattr(new_org, 'description', None),
        "seeking_tags": getattr(new_org, 'seeking_tags', None)
    }

@app.get("/api/organizations/{org_id}", tags=["Organizations"])
def get_organization(org_id: str, db: Session = Depends(get_db)):
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Return as simple dictionary to avoid validation errors
    return {
        "id": org.id,
        "name": org.name,
        "type": getattr(org, 'type', None),
        "website_url": getattr(org, 'website_url', None),
        "logo_url": getattr(org, 'logo_url', None),
        "location": getattr(org, 'location', None),
        "description": getattr(org, 'description', None),
        "seeking_tags": getattr(org, 'seeking_tags', None)
    }

# --- TARGETS ENDPOINTS ---

@app.get("/api/targets", tags=["Targets"])
def get_user_targets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.organization_id:
        return []
    
    targets = db.query(models.Target).options(
        joinedload(models.Target.created_by)
    ).filter(
        models.Target.organization_id == current_user.organization_id
    ).order_by(models.Target.created_at.desc()).all()
    
    # Return as simple dictionaries
    return [
        {
            "id": target.id,
            "organization_id": target.organization_id,
            "created_by_id": target.created_by_id,
            "target_organization_name": getattr(target, 'target_organization_name', ''),
            "target_country": getattr(target, 'target_country', None),
            "target_type": getattr(target, 'target_type', None),
            "partnership_type": getattr(target, 'partnership_type', None),
            "contact_person": getattr(target, 'contact_person', None),
            "contact_email": getattr(target, 'contact_email', None),
            "website": getattr(target, 'website', None),
            "priority": getattr(target, 'priority', 'MEDIUM'),
            "stage": getattr(target, 'stage', 'RESEARCH'),
            "notes": getattr(target, 'notes', None),
            "next_action": getattr(target, 'next_action', None),
            "reminder_date": getattr(target, 'reminder_date', None),
            "created_at": target.created_at.isoformat() if target.created_at else None,
            "created_by": {
                "id": target.created_by.id,
                "full_name": target.created_by.full_name
            } if target.created_by else None
        }
        for target in targets
    ]

@app.post("/api/targets", tags=["Targets"])
def create_target(
    target: schemas.TargetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    new_target = models.Target(
        id=str(uuid.uuid4()),
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
        **target.model_dump()
    )
    
    db.add(new_target)
    db.commit()
    db.refresh(new_target)
    
    # Load the created_by relationship
    db.refresh(new_target, ['created_by'])
    
    # Return as simple dictionary
    return {
        "id": new_target.id,
        "organization_id": new_target.organization_id,
        "created_by_id": new_target.created_by_id,
        "target_organization_name": getattr(new_target, 'target_organization_name', ''),
        "target_country": getattr(new_target, 'target_country', None),
        "target_type": getattr(new_target, 'target_type', None),
        "partnership_type": getattr(new_target, 'partnership_type', None),
        "contact_person": getattr(new_target, 'contact_person', None),
        "contact_email": getattr(new_target, 'contact_email', None),
        "website": getattr(new_target, 'website', None),
        "priority": getattr(new_target, 'priority', 'MEDIUM'),
        "stage": getattr(new_target, 'stage', 'RESEARCH'),
        "notes": getattr(new_target, 'notes', None),
        "next_action": getattr(new_target, 'next_action', None),
        "reminder_date": getattr(new_target, 'reminder_date', None),
        "created_at": new_target.created_at.isoformat() if new_target.created_at else None,
        "created_by": {
            "id": new_target.created_by.id,
            "full_name": new_target.created_by.full_name
        } if new_target.created_by else None
    }

@app.get("/api/targets/{target_id}", tags=["Targets"])
def get_target(
    target_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    target = db.query(models.Target).options(
        joinedload(models.Target.created_by)
    ).filter(models.Target.id == target_id).first()
    
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # Check if current user's org owns this target
    if target.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Return as simple dictionary
    return {
        "id": target.id,
        "organization_id": target.organization_id,
        "created_by_id": target.created_by_id,
        "target_organization_name": getattr(target, 'target_organization_name', ''),
        "target_country": getattr(target, 'target_country', None),
        "target_type": getattr(target, 'target_type', None),
        "partnership_type": getattr(target, 'partnership_type', None),
        "contact_person": getattr(target, 'contact_person', None),
        "contact_email": getattr(target, 'contact_email', None),
        "website": getattr(target, 'website', None),
        "priority": getattr(target, 'priority', 'MEDIUM'),
        "stage": getattr(target, 'stage', 'RESEARCH'),
        "notes": getattr(target, 'notes', None),
        "next_action": getattr(target, 'next_action', None),
        "reminder_date": getattr(target, 'reminder_date', None),
        "created_at": target.created_at.isoformat() if target.created_at else None,
        "created_by": {
            "id": target.created_by.id,
            "full_name": target.created_by.full_name
        } if target.created_by else None
    }

@app.put("/api/targets/{target_id}", tags=["Targets"])
def update_target(
    target_id: str,
    target_update: schemas.TargetUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    target = db.query(models.Target).filter(models.Target.id == target_id).first()
    
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # Check if current user's org owns this target
    if target.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update target fields
    update_data = target_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(target, field, value)
    
    target.updated_at = datetime.now()
    
    db.commit()
    db.refresh(target)
    
    # Load the created_by relationship
    db.refresh(target, ['created_by'])
    
    # Return as simple dictionary
    return {
        "id": target.id,
        "organization_id": target.organization_id,
        "created_by_id": target.created_by_id,
        "target_organization_name": getattr(target, 'target_organization_name', ''),
        "target_country": getattr(target, 'target_country', None),
        "target_type": getattr(target, 'target_type', None),
        "partnership_type": getattr(target, 'partnership_type', None),
        "contact_person": getattr(target, 'contact_person', None),
        "contact_email": getattr(target, 'contact_email', None),
        "website": getattr(target, 'website', None),
        "priority": getattr(target, 'priority', 'MEDIUM'),
        "stage": getattr(target, 'stage', 'RESEARCH'),
        "notes": getattr(target, 'notes', None),
        "next_action": getattr(target, 'next_action', None),
        "reminder_date": getattr(target, 'reminder_date', None),
        "created_at": target.created_at.isoformat() if target.created_at else None,
        "updated_at": target.updated_at.isoformat() if target.updated_at else None,
        "created_by": {
            "id": target.created_by.id,
            "full_name": target.created_by.full_name
        } if target.created_by else None
    }

@app.delete("/api/targets/{target_id}", tags=["Targets"])
def delete_target(
    target_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    target = db.query(models.Target).filter(models.Target.id == target_id).first()
    
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # Check if current user's org owns this target
    if target.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(target)
    db.commit()
    
    return {"message": "Target deleted successfully"}

# --- PARTNERSHIPS ENDPOINTS ---

@app.get("/api/partnerships", tags=["Partnerships"])
def get_user_partnerships(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.organization_id:
        return []
    
    # Get partnerships where current user's org is involved with eager loading
    partnerships = db.query(models.Partnership).options(
        joinedload(models.Partnership.organization_one),
        joinedload(models.Partnership.organization_two),
        joinedload(models.Partnership.internal_manager)
    ).filter(
        (models.Partnership.organization_one_id == current_user.organization_id) |
        (models.Partnership.organization_two_id == current_user.organization_id)
    ).all()
    
    result = []
    for partnership in partnerships:
        # Determine which org is the "partner" (not the current user's org)
        if partnership.organization_one_id == current_user.organization_id:
            partner_org = partnership.organization_two
        else:
            partner_org = partnership.organization_one
            
        # Safety check in case relationship loading failed
        if partner_org is None:
            if partnership.organization_one_id == current_user.organization_id:
                partner_org = db.query(models.Organization).filter(
                    models.Organization.id == partnership.organization_two_id
                ).first()
            else:
                partner_org = db.query(models.Organization).filter(
                    models.Organization.id == partnership.organization_one_id
                ).first()
            
        # Skip if we still can't find partner org
        if partner_org is None:
            continue
            
        result.append({
            "id": partnership.id,
            "status": partnership.status,
            "agreement_end_date": partnership.agreement_end_date.isoformat() if partnership.agreement_end_date else None,
            "agreement_type": getattr(partnership, 'agreement_type', None),
            "partner_organization": {
                "id": partner_org.id,
                "name": partner_org.name
            },
            "internal_manager": {
                "id": partnership.internal_manager.id,
                "full_name": partnership.internal_manager.full_name
            } if partnership.internal_manager else None,
            "documents": []
        })
    
    return result

@app.post("/api/partnerships", tags=["Partnerships"])
def create_partnership(
    partnership: schemas.PartnershipCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    new_partnership = models.Partnership(
        id=str(uuid.uuid4()),
        organization_one_id=current_user.organization_id,
        organization_two_id=partnership.organization_two_id,
        status="PENDING",
        agreement_type=partnership.agreement_type,
        agreement_end_date=partnership.agreement_end_date,
        internal_manager_id=current_user.id,
        created_at=datetime.now()
    )
    
    db.add(new_partnership)
    db.commit()
    db.refresh(new_partnership)
    
    # Return the same format as get_partnerships
    partner_org = db.query(models.Organization).filter(
        models.Organization.id == partnership.organization_two_id
    ).first()
    
    # Safety check
    if partner_org is None:
        raise HTTPException(status_code=404, detail="Partner organization not found")
    
    return {
        "id": new_partnership.id,
        "status": new_partnership.status,
        "agreement_end_date": new_partnership.agreement_end_date.isoformat() if new_partnership.agreement_end_date else None,
        "agreement_type": getattr(new_partnership, 'agreement_type', None),
        "partner_organization": {
            "id": partner_org.id,
            "name": partner_org.name
        },
        "internal_manager": {
            "id": current_user.id,
            "full_name": current_user.full_name
        },
        "documents": []
    }

@app.get("/api/partnerships/{partnership_id}", tags=["Partnerships"])
def get_partnership(
    partnership_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    partnership = db.query(models.Partnership).options(
        joinedload(models.Partnership.organization_one),
        joinedload(models.Partnership.organization_two),
        joinedload(models.Partnership.internal_manager)
    ).filter(models.Partnership.id == partnership_id).first()
    
    if not partnership:
        raise HTTPException(status_code=404, detail="Partnership not found")
    
    # Check if current user's org is involved in this partnership
    if (partnership.organization_one_id != current_user.organization_id and 
        partnership.organization_two_id != current_user.organization_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Return the partnership in the same format as the list endpoint
    if partnership.organization_one_id == current_user.organization_id:
        partner_org = partnership.organization_two
        current_org = partnership.organization_one
    else:
        partner_org = partnership.organization_one
        current_org = partnership.organization_two
        
    # Safety check in case relationship loading failed
    if partner_org is None:
        if partnership.organization_one_id == current_user.organization_id:
            partner_org = db.query(models.Organization).filter(
                models.Organization.id == partnership.organization_two_id
            ).first()
        else:
            partner_org = db.query(models.Organization).filter(
                models.Organization.id == partnership.organization_one_id
            ).first()
    
    if current_org is None:
        if partnership.organization_one_id == current_user.organization_id:
            current_org = db.query(models.Organization).filter(
                models.Organization.id == partnership.organization_one_id
            ).first()
        else:
            current_org = db.query(models.Organization).filter(
                models.Organization.id == partnership.organization_two_id
            ).first()
    
    if partner_org is None or current_org is None:
        raise HTTPException(status_code=404, detail="Organization data not found")
    
    return {
        "id": partnership.id,
        "status": partnership.status,
        "agreement_type": getattr(partnership, 'agreement_type', None),
        "agreement_end_date": partnership.agreement_end_date.isoformat() if partnership.agreement_end_date else None,
        "partner_organization": {
            "id": partner_org.id,
            "name": partner_org.name
        },
        "organization_one": {
            "id": current_org.id,
            "name": current_org.name
        },
        "internal_manager": {
            "id": partnership.internal_manager.id,
            "full_name": partnership.internal_manager.full_name
        } if partnership.internal_manager else None,
        "created_at": partnership.created_at.isoformat() if partnership.created_at else None,
        "updated_at": partnership.updated_at.isoformat() if partnership.updated_at else None,
        "documents": []
    }

# PARTNERSHIP STATUS UPDATE ENDPOINT
@app.put("/api/partnerships/{partnership_id}/status", tags=["Partnerships"])
def update_partnership_status(
    partnership_id: str,
    status_data: dict,  # Accept JSON body with status and notes
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update partnership status (for accept/decline functionality)"""
    partnership = db.query(models.Partnership).filter(models.Partnership.id == partnership_id).first()
    
    if not partnership:
        raise HTTPException(status_code=404, detail="Partnership not found")
    
    # Check if current user's org is involved in this partnership
    if (partnership.organization_one_id != current_user.organization_id and 
        partnership.organization_two_id != current_user.organization_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate status
    valid_statuses = ["PENDING", "ACTIVE", "DECLINED", "EXPIRED"]
    new_status = status_data.get("status")
    
    if not new_status or new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    # Update partnership status
    partnership.status = new_status
    partnership.updated_at = datetime.now()
    
    db.commit()
    db.refresh(partnership)
    
    return {"message": f"Partnership status updated to {new_status}", "status": new_status}

# PARTNERSHIP DELETE ENDPOINT
@app.delete("/api/partnerships/{partnership_id}", tags=["Partnerships"])
def delete_partnership(
    partnership_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Remove/delete a partnership"""
    partnership = db.query(models.Partnership).filter(models.Partnership.id == partnership_id).first()
    
    if not partnership:
        raise HTTPException(status_code=404, detail="Partnership not found")
    
    # Check if current user's org is involved in this partnership
    if (partnership.organization_one_id != current_user.organization_id and 
        partnership.organization_two_id != current_user.organization_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete the partnership
    db.delete(partnership)
    db.commit()
    
    return {"message": "Partnership removed successfully"}