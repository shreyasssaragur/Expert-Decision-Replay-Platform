from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session
from sqlalchemy import func

from datetime import datetime, timedelta, timezone

import os
import shutil

# ==========================
# Database
# ==========================

from database import (
    Base,
    engine,
    get_db,
)


# ==========================
# Models
# ==========================

from models import (
    User,
    Decision,
    Alternative,
    Criteria,
    AlternativeScore,
    Document,
    Discussion,
    DecisionVersion,
    Approval,
    Notification,
    AuditLog,
)


# ==========================
# Schemas
# ==========================

from schemas import (
    UserRegister,
    UserLogin,
    UserUpdate,
    RoleUpdate,

    DecisionCreate,
    DecisionUpdate,

    AlternativeCreate,
    AlternativeUpdate,

    CriteriaCreate,
    CriteriaUpdate,

    AlternativeScoreCreate,
    AlternativeScoreUpdate,

    DiscussionCreate,
    DiscussionUpdate,

    DecisionVersionCreate,
    DecisionVersionUpdate,

    ApprovalCreate,
    ApprovalUpdate,
    ApprovalResponse,

    AuditLogCreate,
    AuditLogResponse,

    
)


# ==========================
# Security
# ==========================

from security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_role,
    validate_role,
)

# =====================================
# FastAPI App
# =====================================

app = FastAPI(
    title="Expert Decision Replay Platform"
)
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_FOLDER),
    name="uploads"
)
# =====================================
# CORS
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://expert-decision-replay-frontend-mbh7.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================
# Create Tables
# =====================================

Base.metadata.create_all(bind=engine)
# =====================================
# Upload Directory
# =====================================

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

# =====================================
# Home API
# =====================================

@app.get("/")
def home():
    return {
        "message": "Database Connected Successfully"
    }

# =====================================
# Register User
# =====================================

@app.post("/register")
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.user_id
    }

# =====================================
# Login User
# =====================================

@app.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    # Check Email
    db_user = (
        db.query(User)
        .filter(
            User.email == user.email
        )
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email"
        )

    # Check Password
    if not verify_password(
        user.password,
        db_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    # Create JWT Token
    access_token = create_access_token(
        db_user.user_id
    )

    # ============================================================
    # Create Audit Log
    # ============================================================

    create_audit_log(

        db=db,

        user_id=db_user.user_id,

        decision_id=None,

        action_type="Login",

        description=f'{db_user.username} logged into the system.'

    )

    # Return Login Response
    return {

        "message": "Login Successful",

        "access_token": access_token,

        "token_type": "bearer",

        "user_id": db_user.user_id,

        "username": db_user.username,

        "role": db_user.role

    }


# =====================================
# Update User
# =====================================

@app.put("/users/{user_id}")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.username = user_data.username
    user.email = user_data.email

    db.commit()
    db.refresh(user)

    return {
        "message": "User updated successfully"
    }
# =====================================
# Get Current Logged-In User
# =====================================

@app.get("/me")
def get_me(
    current_user: User = Depends(
        get_current_user
    )
):

    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }


# =====================================
# Delete User
# =====================================

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }


# =====================================
# Update User Role
# =====================================

@app.put("/users/{user_id}/role")
def update_role(
    user_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    allowed_roles = [
        "Admin",
        "Manager",
        "Reviewer",
        "User"
    ]

    if role_data.role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    user.role = role_data.role

    db.commit()
    db.refresh(user)

    return {
        "message": "Role updated successfully",
        "role": user.role
    }
# ============================================================
# Get All Users
# ============================================================

@app.get("/users")
def get_users(
    db: Session = Depends(get_db)
):

    users = (
        db.query(User)
        .order_by(User.user_id)
        .all()
    )

    return users

# =====================================
# Create Decision + Initial Version
# =====================================

@app.post("/decisions")
def create_decision(
    decision: DecisionCreate,
    db: Session = Depends(get_db)
):

    # Check user exists
    user = (
        db.query(User)
        .filter(
            User.user_id == decision.user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Create decision
    new_decision = Decision(
        user_id=decision.user_id,
        decision_title=decision.decision_title,
        decision_description=decision.decision_description
    )

    try:

        db.add(new_decision)

        # Generate decision_id
        db.flush()

        # Create Initial Version
        initial_version = DecisionVersion(
            decision_id=new_decision.decision_id,
            version_number=1,
            title=new_decision.decision_title,
            description=new_decision.decision_description,
            status="Draft",
            modified_by=decision.user_id,
            change_summary="Initial decision created"
        )

        db.add(initial_version)

        # Save Decision & Version
        db.commit()

        db.refresh(new_decision)
        db.refresh(initial_version)

        # ============================================================
        # Audit Log
        # ============================================================

        create_audit_log(

            db=db,

            user_id=decision.user_id,

            decision_id=new_decision.decision_id,

            action_type="Create Decision",

            description=f'Decision "{new_decision.decision_title}" created successfully.'

        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not create decision: {str(e)}"
        )

    return {

        "message":
            "Decision created successfully",

        "decision_id":
            new_decision.decision_id,

        "version_number":
            initial_version.version_number,

        "status":
            initial_version.status,

        "change_summary":
            initial_version.change_summary

    }
# =====================================
# Get All Decisions
# =====================================

@app.get("/decisions")
def get_decisions(
    db: Session = Depends(get_db)
):
    decisions = (
        db.query(Decision)
        .order_by(Decision.decision_id.desc())
        .all()
    )

    return decisions
# =====================================
# Get Single Decision
# =====================================

@app.get("/decisions/{decision_id}")
def get_single_decision(
    decision_id: int,
    db: Session = Depends(get_db)
):

    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    # Get the user who created the decision
    creator = (
        db.query(User)
        .filter(
            User.user_id == decision.user_id
        )
        .first()
    )

    return {
        "decision_id": decision.decision_id,
        "decision_title": decision.decision_title,
        "decision_description": decision.decision_description,
        "user_id": decision.user_id,
        "created_by": (
            creator.username
            if creator
            else f"User ID: {decision.user_id}"
        )
    }
# =====================================
# Update Decision + Automatic Version
# =====================================

@app.put("/decisions/{decision_id}")
def update_decision(
    decision_id: int,
    decision_data: DecisionVersionUpdate,
    db: Session = Depends(get_db)
):

    # Find decision
    decision = (
        db.query(Decision)
        .filter(Decision.decision_id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    # Check modifying user exists
    user = (
        db.query(User)
        .filter(User.user_id == decision_data.modified_by)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check whether title or description changed
    if (
        decision.decision_title == decision_data.decision_title
        and
        decision.decision_description == decision_data.decision_description
    ):
        raise HTTPException(
            status_code=400,
            detail="No changes detected in decision"
        )

    # Find latest version
    latest_version = (
        db.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.version_number.desc())
        .first()
    )

    # Automatically calculate next version number
    next_version = (
        latest_version.version_number + 1
        if latest_version
        else 1
    )

    # Update current decision
    decision.decision_title = decision_data.decision_title
    decision.decision_description = decision_data.decision_description

    # Create version history record
    new_version = DecisionVersion(
        decision_id=decision_id,
        version_number=next_version,
        title=decision_data.decision_title,
        description=decision_data.decision_description,
        status=decision_data.status,
        modified_by=decision_data.modified_by,
        change_summary=decision_data.change_summary
    )

    try:
        db.add(new_version)

        # One commit updates decision AND creates version
        db.commit()

        db.refresh(decision)
        db.refresh(new_version)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not update decision and create version: {str(e)}"
        )

    return {
        "message": "Decision updated and version created successfully",
        "decision_id": decision.decision_id,
        "decision_title": decision.decision_title,
        "decision_description": decision.decision_description,
        "version_number": new_version.version_number,
        "status": new_version.status,
        "modified_by": new_version.modified_by,
        "modified_at": new_version.modified_at,
        "change_summary": new_version.change_summary
    }

# =====================================
# Delete Decision
# =====================================

@app.delete("/decisions/{decision_id}")
def delete_decision(
    decision_id: int,
    db: Session = Depends(get_db)
):

    # Check decision exists
    decision = (
        db.query(Decision)
        .filter(Decision.decision_id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    # Store values before deleting
    decision_title = decision.decision_title
    decision_owner = decision.user_id

    try:

        db.delete(decision)

        db.commit()

        # ============================================================
        # Audit Log
        # ============================================================

        create_audit_log(

            db=db,

            user_id=decision_owner,

            decision_id=decision_id,

            action_type="Delete Decision",

            description=(
                f'Decision "{decision_title}" deleted successfully.'
            )

        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not delete decision: {str(e)}"
        )

    return {
        "message": "Decision deleted successfully"
    }


@app.get("/alternatives")
def get_alternatives(
    db: Session = Depends(get_db)
):
    return db.query(Alternative).all()


@app.get("/alternatives/{alternative_id}")
def get_alternative(
    alternative_id: int,
    db: Session = Depends(get_db)
):

    alternative = (
        db.query(Alternative)
        .filter(
            Alternative.alternative_id == alternative_id
        )
        .first()
    )

    if not alternative:
        raise HTTPException(
            status_code=404,
            detail="Alternative not found"
        )

    return alternative


# ============================================================
# Create Alternative
# ============================================================

@app.post("/alternatives")
def create_alternative(
    alternative: AlternativeCreate,
    db: Session = Depends(get_db)
):

    new_alternative = Alternative(
        decision_id=alternative.decision_id,
        alternative_name=alternative.alternative_name,
        description=alternative.description,
        pros=alternative.pros,
        cons=alternative.cons,
        estimated_cost=alternative.estimated_cost,
        feasibility=alternative.feasibility,
        risk_level=alternative.risk_level
    )

    db.add(new_alternative)
    db.commit()
    db.refresh(new_alternative)

    return new_alternative
# =====================================
# Update Alternative
# =====================================

@app.put("/alternatives/{alternative_id}")
def update_alternative(
    alternative_id: int,
    alternative_data: AlternativeUpdate,
    db: Session = Depends(get_db)
):

    alternative = (
        db.query(Alternative)
        .filter(
            Alternative.alternative_id == alternative_id
        )
        .first()
    )

    if not alternative:
        raise HTTPException(
            status_code=404,
            detail="Alternative not found"
        )

    alternative.alternative_name = alternative_data.alternative_name
    alternative.description = alternative_data.description
    alternative.pros = alternative_data.pros
    alternative.cons = alternative_data.cons
    alternative.estimated_cost = alternative_data.estimated_cost
    alternative.feasibility = alternative_data.feasibility
    alternative.risk_level = alternative_data.risk_level

    db.commit()
    db.refresh(alternative)

    return {
        "message": "Alternative updated successfully"
    }


# =====================================
# Delete Alternative
# =====================================

@app.delete("/alternatives/{alternative_id}")
def delete_alternative(
    alternative_id: int,
    db: Session = Depends(get_db)
):

    alternative = (
        db.query(Alternative)
        .filter(
            Alternative.alternative_id == alternative_id
        )
        .first()
    )

    if not alternative:
        raise HTTPException(
            status_code=404,
            detail="Alternative not found"
        )

    db.delete(alternative)
    db.commit()

    return {
        "message": "Alternative deleted successfully"
    }




# =====================================
# Create Criteria
# =====================================

@app.post("/criteria")
def create_criteria(
    criteria: CriteriaCreate,
    db: Session = Depends(get_db)
):

    # Check decision exists
    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == criteria.decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    new_criteria = Criteria(
        decision_id=criteria.decision_id,
        criteria_name=criteria.criteria_name,
        weight=criteria.weight
    )

    db.add(new_criteria)
    db.commit()
    db.refresh(new_criteria)

    return {
        "message": "Criteria created successfully",
        "criteria_id": new_criteria.criteria_id
    }

# =====================================
# Get All Criteria
# =====================================

@app.get("/criteria")
def get_criteria(
    db: Session = Depends(get_db)
):
    return db.query(Criteria).all()

# =====================================
# Create Alternative Score
# =====================================

@app.post("/alternative-scores")
def create_alternative_score(
    score: AlternativeScoreCreate,
    db: Session = Depends(get_db)
):

    alternative = (
        db.query(Alternative)
        .filter(
            Alternative.alternative_id == score.alternative_id
        )
        .first()
    )

    if not alternative:
        raise HTTPException(
            status_code=404,
            detail="Alternative not found"
        )

    criteria = (
        db.query(Criteria)
        .filter(
            Criteria.criteria_id == score.criteria_id
        )
        .first()
    )

    if not criteria:
        raise HTTPException(
            status_code=404,
            detail="Criteria not found"
        )

    new_score = AlternativeScore(
        alternative_id=score.alternative_id,
        criteria_id=score.criteria_id,
        score=score.score
    )

    db.add(new_score)
    db.commit()
    db.refresh(new_score)

    return {
        "message": "Score created successfully",
        "score_id": new_score.score_id
    }


@app.get("/alternative-scores")
def get_alternative_scores(
    db: Session = Depends(get_db)
):
    return db.query(AlternativeScore).all()


@app.put("/alternative-scores/{score_id}")
def update_alternative_score(
    score_id: int,
    score_data: AlternativeScoreUpdate,
    db: Session = Depends(get_db)
):

    score = (
        db.query(AlternativeScore)
        .filter(
            AlternativeScore.score_id == score_id
        )
        .first()
    )

    if not score:
        raise HTTPException(
            status_code=404,
            detail="Score not found"
        )

    score.score = score_data.score

    db.commit()
    db.refresh(score)

    return {
        "message": "Score updated successfully"
    }


@app.delete("/alternative-scores/{score_id}")
def delete_alternative_score(
    score_id: int,
    db: Session = Depends(get_db)
):

    score = (
        db.query(AlternativeScore)
        .filter(
            AlternativeScore.score_id == score_id
        )
        .first()
    )

    if not score:
        raise HTTPException(
            status_code=404,
            detail="Score not found"
        )

    db.delete(score)
    db.commit()

    return {
        "message": "Score deleted successfully"
    }
# ============================================================
# GET SCORES BY DECISION
# ============================================================

@app.get("/decisions/{decision_id}/scores")
def get_decision_scores(
    decision_id: int,
    db: Session = Depends(get_db)
):

    # Check decision exists
    decision = (
        db.query(Decision)
        .filter(Decision.decision_id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found."
        )

    scores = (

        db.query(
            AlternativeScore.score_id,
            Alternative.alternative_name,
            Criteria.criteria_name,
            AlternativeScore.alternative_id,
            AlternativeScore.criteria_id,
            AlternativeScore.score
        )

        .join(
            Alternative,
            Alternative.alternative_id ==
            AlternativeScore.alternative_id
        )

        .join(
            Criteria,
            Criteria.criteria_id ==
            AlternativeScore.criteria_id
        )

        .filter(
            Alternative.decision_id == decision_id
        )

        .order_by(
            Alternative.alternative_name,
            Criteria.criteria_name
        )

        .all()

    )

    return [
    {
        "score_id": row.score_id,
        "alternative_id": row.alternative_id,
        "criteria_id": row.criteria_id,
        "alternative_name": row.alternative_name,
        "criteria_name": row.criteria_name,
        "score": float(row.score)
    }
    for row in scores
]
# =====================================
# Get Single Criteria
# =====================================

@app.get("/criteria/{criteria_id}")
def get_criteria_by_id(
    criteria_id: int,
    db: Session = Depends(get_db)
):

    criteria = (
        db.query(Criteria)
        .filter(
            Criteria.criteria_id == criteria_id
        )
        .first()
    )

    if not criteria:
        raise HTTPException(
            status_code=404,
            detail="Criteria not found"
        )

    return criteria

# =====================================
# Update Criteria
# =====================================

@app.put("/criteria/{criteria_id}")
def update_criteria(
    criteria_id: int,
    criteria_data: CriteriaUpdate,
    db: Session = Depends(get_db)
):

    criteria = (
        db.query(Criteria)
        .filter(
            Criteria.criteria_id == criteria_id
        )
        .first()
    )

    if not criteria:
        raise HTTPException(
            status_code=404,
            detail="Criteria not found"
        )

    criteria.criteria_name = criteria_data.criteria_name
    criteria.weight = criteria_data.weight

    db.commit()
    db.refresh(criteria)

    return {
        "message": "Criteria updated successfully"
    }

# =====================================
# Delete Criteria
# =====================================

@app.delete("/criteria/{criteria_id}")
def delete_criteria(
    criteria_id: int,
    db: Session = Depends(get_db)
):

    criteria = (
        db.query(Criteria)
        .filter(
            Criteria.criteria_id == criteria_id
        )
        .first()
    )

    if not criteria:
        raise HTTPException(
            status_code=404,
            detail="Criteria not found"
        )

    db.delete(criteria)
    db.commit()

    return {
        "message": "Criteria deleted successfully"
    }
# ============================================================
# Recommendation Engine
# ============================================================

@app.get("/decisions/{decision_id}/recommendation")
def get_recommendation(
    decision_id: int,
    db: Session = Depends(get_db)
):

    # ----------------------------------------
    # Check Decision Exists
    # ----------------------------------------

    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found."
        )

    # ----------------------------------------
    # Get Alternatives
    # ----------------------------------------

    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .all()
    )

    if not alternatives:
        raise HTTPException(
            status_code=404,
            detail="No alternatives found."
        )

    results = []

    criteria_used = 0

    # ----------------------------------------
    # Calculate Score
    # ----------------------------------------

    for alt in alternatives:

        scores = (

            db.query(
                AlternativeScore,
                Criteria
            )

            .join(
                Criteria,
                AlternativeScore.criteria_id ==
                Criteria.criteria_id
            )

            .filter(
                AlternativeScore.alternative_id ==
                alt.alternative_id
            )

            .all()

        )

        total_score = 0

        criteria_used = len(scores)

        for score, criteria in scores:

            total_score += score.score
                

        results.append({

            "alternative_id": alt.alternative_id,

            "alternative_name": alt.alternative_name,

            "total_score": total_score

        })

    # ----------------------------------------
    # Sort Highest Score First
    # ----------------------------------------

    results.sort(
        key=lambda x: x["total_score"],
        reverse=True
    )

    # ----------------------------------------
    # Ranking
    # ----------------------------------------

    for index, item in enumerate(results):

        item["rank"] = index + 1

    # ----------------------------------------
    # Final Response
    # ----------------------------------------

    return {

        "decision": decision.decision_title,

        "recommended_alternative": results[0],

        "reason":
        "Highest weighted score based on selected criteria.",

        "criteria_used": criteria_used,

        "total_alternatives": len(alternatives),

        "all_alternatives": results

    }
# =====================================
# DOCUMENT MANAGEMENT
# =====================================


# =====================================
# Upload Document
# =====================================

@app.post("/decisions/{decision_id}/documents")
def upload_document(
    decision_id: int,
    uploaded_by: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Check if decision exists
    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    # Check if user exists
    user = (
        db.query(User)
        .filter(
            User.user_id == uploaded_by
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Get safe filename
    original_file_name = os.path.basename(
        file.filename
    )

    # Create filename for storage
    stored_file_name = (
        f"{decision_id}_{original_file_name}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        stored_file_name
    )

    # Prevent overwriting existing files
    counter = 1

    while os.path.exists(file_path):

        name, extension = os.path.splitext(
            original_file_name
        )

        stored_file_name = (
            f"{decision_id}_{name}_{counter}{extension}"
        )

        file_path = os.path.join(
            UPLOAD_DIR,
            stored_file_name
        )

        counter += 1

    # Save physical file
    try:

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Could not save file"
        )

    finally:

        file.file.close()

    # Save file information in database
    new_document = Document(
        decision_id=decision_id,
        file_name=original_file_name,
        file_path=file_path,
        file_type=file.content_type,
        uploaded_by=uploaded_by
    )

    try:

        db.add(new_document)
        db.commit()
        db.refresh(new_document)

    except Exception:

        db.rollback()

        # Remove physical file if DB save fails
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail="Could not save document information"
        )

    return {
        "message": "File uploaded successfully",
        "document_id": new_document.document_id,
        "decision_id": new_document.decision_id,
        "file_name": new_document.file_name,
        "file_type": new_document.file_type,
        "uploaded_by": new_document.uploaded_by,
        "uploaded_at": new_document.uploaded_at
    }


# =====================================
# View All Documents For Decision
# =====================================

@app.get("/decisions/{decision_id}/documents")
def get_decision_documents(
    decision_id: int,
    db: Session = Depends(get_db)
):

    # Check decision exists
    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    documents = (
        db.query(Document)
        .filter(
            Document.decision_id == decision_id
        )
        .all()
    )

    return documents


# =====================================
# View Single Document Information
# =====================================

@app.get("/documents/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = (
        db.query(Document)
        .filter(
            Document.document_id == document_id
        )
        .first()
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


# =====================================
# Download Document
# =====================================

@app.get("/documents/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = (
        db.query(Document)
        .filter(
            Document.document_id == document_id
        )
        .first()
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Check physical file exists
    if not os.path.exists(
        document.file_path
    ):

        raise HTTPException(
            status_code=404,
            detail="File not found on server"
        )

    return FileResponse(
        path=document.file_path,
        filename=document.file_name,
        media_type=(
            document.file_type
            or "application/octet-stream"
        )
    )


# =====================================
# Delete Document
# =====================================

@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = (
        db.query(Document)
        .filter(
            Document.document_id == document_id
        )
        .first()
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    file_path = document.file_path
    file_name = document.file_name
    decision_id = document.decision_id
    uploaded_by = document.uploaded_by

    # Get decision title for audit log
    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == decision_id
        )
        .first()
    )

    decision_title = (
        decision.decision_title
        if decision
        else f"Decision ID {decision_id}"
    )

    # Delete database record
    try:

        db.delete(document)

        db.commit()

        # ============================================================
        # Audit Log
        # ============================================================

        create_audit_log(

            db=db,

            user_id=uploaded_by,

            decision_id=decision_id,

            action_type="Delete Document",

            description=(
                f'Deleted document "{file_name}" '
                f'from decision "{decision_title}".'
            )

        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not delete document: {str(e)}"
        )

    # Delete physical file
    if os.path.exists(file_path):

        try:

            os.remove(file_path)

        except OSError:

            return {

                "message":
                    "Document record deleted, but physical file could not be removed",

                "file_name": file_name

            }

    return {

        "message": "Document deleted successfully",

        "file_name": file_name

    }

# =====================================
# DISCUSSION MODULE APIs
# =====================================

# Add Comment or Meeting Note
@app.post("/decisions/{decision_id}/discussions")
def create_discussion(
    decision_id: int,
    discussion: DiscussionCreate,
    db: Session = Depends(get_db)
):
    # Check decision exists
    decision = db.query(Decision).filter(
        Decision.decision_id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    # Check user exists
    user = db.query(User).filter(
        User.user_id == discussion.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Validate type
    if discussion.discussion_type not in ["Comment", "Meeting Note"]:
        raise HTTPException(
            status_code=400,
            detail="Type must be Comment or Meeting Note"
        )

    new_discussion = Discussion(
        decision_id=decision_id,
        user_id=discussion.user_id,
        comment=discussion.comment,
        discussion_type=discussion.discussion_type
    )

    db.add(new_discussion)
    db.commit()
    db.refresh(new_discussion)

    return {
        "message": "Discussion added successfully",
        "discussion_id": new_discussion.discussion_id,
        "decision_id": new_discussion.decision_id,
        "user_id": new_discussion.user_id,
        "comment": new_discussion.comment,
        "discussion_type": new_discussion.discussion_type,
        "created_at": new_discussion.created_at
    }


# View All Discussions of a Decision
@app.get("/decisions/{decision_id}/discussions")
def get_discussions(
    decision_id: int,
    db: Session = Depends(get_db)
):
    decision = db.query(Decision).filter(
        Decision.decision_id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return db.query(Discussion).filter(
        Discussion.decision_id == decision_id
    ).order_by(
        Discussion.created_at.desc()
    ).all()


# View One Discussion
@app.get("/discussions/{discussion_id}")
def get_discussion(
    discussion_id: int,
    db: Session = Depends(get_db)
):
    discussion = db.query(Discussion).filter(
        Discussion.discussion_id == discussion_id
    ).first()

    if not discussion:
        raise HTTPException(
            status_code=404,
            detail="Discussion not found"
        )

    return discussion





# =====================================
# DECISION VERSION TRACKING
# =====================================


from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session


@app.post(
    "/decisions/{decision_id}/versions", status_code=status.HTTP_201_CREATED
)
def create_decision_version(
    decision_id: int,
    version_data: DecisionVersionCreate,
    db: Session = Depends(get_db),
):
    # 1. Check decision
    decision = (
        db.query(Decision).filter(Decision.decision_id == decision_id).first()
    )
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found"
        )

    # 2. Check modifying user
    user = (
        db.query(User).filter(User.user_id == version_data.modified_by).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # 3. Find latest version & compute next version number
    latest_version = (
        db.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.version_number.desc())
        .first()
    )
    next_version = (latest_version.version_number + 1) if latest_version else 1

    # 4. Create new version entity
    new_version = DecisionVersion(
        decision_id=decision_id,
        version_number=next_version,
        title=decision.decision_title,
        description=decision.decision_description,
        status=version_data.status,
        modified_by=version_data.modified_by,
        change_summary=version_data.change_summary,
    )

    db.add(new_version)
    db.commit()
    db.refresh(new_version)

    # 5. Create audit log entry
    create_audit_log(
        db=db,
        user_id=version_data.modified_by,
        decision_id=decision.decision_id,
        action_type="Create Version",
        description=(
            f"Created Version {new_version.version_number} "
            f'for decision "{decision.decision_title}".'
        ),
    )

    # 6. Return response
    return {
        "message": "Decision version created successfully",
        "id": new_version.id,
        "decision_id": new_version.decision_id,
        "version_number": new_version.version_number,
        "title": new_version.title,
        "description": new_version.description,
        "status": new_version.status,
        "modified_by": new_version.modified_by,
        "modified_at": new_version.modified_at,
        "change_summary": new_version.change_summary,
    }
# =====================================
# Get Version History
# =====================================

@app.get("/decisions/{decision_id}/versions")
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db)
):

    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    versions = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .all()
    )

    return versions


# =====================================
# Get Specific Version
# =====================================

@app.get(
    "/decisions/{decision_id}/versions/{version_number}"
)
def get_specific_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db)
):

    version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
            DecisionVersion.version_number == version_number
        )
        .first()
    )

    if not version:
        raise HTTPException(
            status_code=404,
            detail="Decision version not found"
        )


    return version


    # ============================================================
# Dashboard Statistics
# ============================================================

@app.get("/dashboard/stats")
def dashboard_stats(
    db: Session = Depends(get_db)
):

    total_decisions = db.query(Decision).count()

    total_alternatives = db.query(Alternative).count()

    total_criteria = db.query(Criteria).count()

    total_users = db.query(User).count()

    total_scores = db.query(AlternativeScore).count()

    return {

        "total_decisions": total_decisions,

        "total_alternatives": total_alternatives,

        "total_criteria": total_criteria,

        "total_users": total_users,

        "total_scores": total_scores

    }

# ============================================================
# Dashboard Charts
# ============================================================

@app.get("/dashboard/charts")
def dashboard_charts(
    db: Session = Depends(get_db)
):

    decisions = db.query(Decision).all()

    chart_data = []

    for decision in decisions:

        alternative_count = (

            db.query(Alternative)

            .filter(

                Alternative.decision_id ==
                decision.decision_id

            )

            .count()

        )

        chart_data.append({

            "decision": decision.decision_title,

            "alternatives": alternative_count

        })

    return chart_data

# ============================================================
# Latest Recommendation
# ============================================================

@app.get("/dashboard/latest-recommendation")
def latest_recommendation(
    db: Session = Depends(get_db)
):

    latest_decision = (

        db.query(Decision)

        .order_by(
            Decision.created_at.desc()
        )

        .first()

    )

    if not latest_decision:

        raise HTTPException(

            status_code=404,

            detail="No decisions available."

        )

    alternatives = (

        db.query(Alternative)

        .filter(
            Alternative.decision_id ==
            latest_decision.decision_id
        )

        .all()

    )

    best = None

    best_score = -1

    for alt in alternatives:

        scores = (

            db.query(
                AlternativeScore,
                Criteria
            )

            .join(
                Criteria,
                AlternativeScore.criteria_id ==
                Criteria.criteria_id
            )

            .filter(
                AlternativeScore.alternative_id ==
                alt.alternative_id
            )

            .all()

        )

        total = 0

        for score, criteria in scores:

            total += (
                score.score *
                criteria.weight
            ) / 100

        if total > best_score:

            best_score = total

            best = alt

    if best is None:

        return {
            "message": "Recommendation not generated yet."
        }

    return {

        "decision": latest_decision.decision_title,

        "recommended_alternative": best.alternative_name,

        "score": round(best_score, 2)

    }

# ============================================================
# Recent Activity
# ============================================================

@app.get("/dashboard/activity")
def dashboard_activity(
    db: Session = Depends(get_db)
):

    recent = (

        db.query(Decision)

        .order_by(
            Decision.created_at.desc()
        )

        .limit(5)

        .all()

    )

    activity = []

    for decision in recent:

        activity.append({

            "type": "Decision",

            "title": decision.decision_title,

            "created_at": decision.created_at

        })

    return activity
# ============================================================
# Upload Document
# ============================================================

@app.post("/documents/upload")
def upload_document(
    decision_id: int = Form(...),
    uploaded_by: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Check decision exists
    decision = (
        db.query(Decision)
        .filter(Decision.decision_id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found."
        )

    # Check user exists
    user = (
        db.query(User)
        .filter(User.user_id == uploaded_by)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    # Original filename
    filename = file.filename

    # Absolute path to save file
    filepath = os.path.abspath(
        os.path.join(
            UPLOAD_FOLDER,
            filename
        )
    )

    try:

        # Save file
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        # Save metadata
        document = Document(

            decision_id=decision_id,

            file_name=filename,

            file_path=filepath,

            file_type=file.content_type,

            uploaded_by=uploaded_by

        )

        db.add(document)

        db.commit()

        db.refresh(document)

        # ============================================================
        # Audit Log
        # ============================================================

        create_audit_log(

            db=db,

            user_id=uploaded_by,

            decision_id=decision_id,

            action_type="Upload Document",

            description=(
                f'Uploaded document "{filename}" '
                f'for decision "{decision.decision_title}".'
            )

        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not upload document: {str(e)}"
        )

    return {

        "message": "Document uploaded successfully.",

        "document_id": document.document_id

    }
# ============================================================
# Get All Documents
# ============================================================

@app.get("/documents")
def get_documents(
    db: Session = Depends(get_db)
):

    documents = (

        db.query(
            Document,
            Decision,
            User
        )

        .join(
            Decision,
            Document.decision_id == Decision.decision_id
        )

        .join(
            User,
            Document.uploaded_by == User.user_id
        )

        .all()

    )

    result = []

    for doc, decision, user in documents:

        result.append({

            "document_id": doc.document_id,

            "decision_id": decision.decision_id,

            "decision_title": decision.decision_title,

            "file_name": doc.file_name,

            "file_type": doc.file_type,

            "file_path": doc.file_path,

            "uploaded_by": user.username,

            "uploaded_at": doc.uploaded_at

        })

    return result

# ============================================================
# Documents By Decision
# ============================================================

@app.get("/decisions/{decision_id}/documents")
def get_documents_by_decision(
    decision_id: int,
    db: Session = Depends(get_db)
):

    docs = (

        db.query(Document)

        .filter(
            Document.decision_id == decision_id
        )

        .all()

    )

    return docs
# ============================================================
# Download Document
# ============================================================

@app.get("/documents/download/{document_id}")
def download_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = (

        db.query(Document)

        .filter(
            Document.document_id == document_id
        )

        .first()

    )

    if not document:

        raise HTTPException(

            status_code=404,

            detail="Document not found."

        )

    if not os.path.exists(document.file_path):

        raise HTTPException(

            status_code=404,

            detail="File does not exist."

        )

    return FileResponse(

        path=document.file_path,

        filename=document.file_name,

        media_type=document.file_type

    )


# ============================================================
# Create Discussion
# ============================================================

@app.post("/discussions")
def create_discussion(
    discussion: DiscussionCreate,
    db: Session = Depends(get_db)
):

    # Check Decision
    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == discussion.decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found."
        )

    # Check User
    user = (
        db.query(User)
        .filter(
            User.user_id == discussion.user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    new_discussion = Discussion(

        decision_id=discussion.decision_id,

        user_id=discussion.user_id,

        comment=discussion.comment

    )

    try:

        db.add(new_discussion)

        db.commit()

        db.refresh(new_discussion)

        # ============================================================
        # Audit Log
        # ============================================================

        create_audit_log(

            db=db,

            user_id=discussion.user_id,

            decision_id=discussion.decision_id,

            action_type="Create Discussion",

            description=(
                f'{user.username} added a discussion '
                f'to decision "{decision.decision_title}".'
            )

        )

    except Exception as e:

        db.rollback()

        raise HTTPException(

            status_code=500,

            detail=f"Could not create discussion: {str(e)}"

        )

    return {

        "message": "Discussion added successfully.",

        "discussion": new_discussion

    }

# ============================================================
# Get All Discussions
# ============================================================

@app.get("/discussions")
def get_discussions(
    db: Session = Depends(get_db)
):

    discussions = (
        db.query(
            Discussion,
            User,
            Decision
        )
        .join(
            User,
            Discussion.user_id == User.user_id
        )
        .join(
            Decision,
            Discussion.decision_id == Decision.decision_id
        )
        .order_by(
            Discussion.created_at.desc()
        )
        .all()
    )

    result = []

    for discussion, user, decision in discussions:

        result.append({

            "discussion_id": discussion.discussion_id,

            "decision_id": decision.decision_id,

            "decision_title": decision.decision_title,

            "user_id": user.user_id,

            "username": user.username,

            "comment": discussion.comment,

            "discussion_type": discussion.discussion_type,

            "created_at": discussion.created_at

        })

    return result

# ============================================================
# Get Discussions by Decision
# ============================================================

@app.get("/decisions/{decision_id}/discussions")
def get_discussions_by_decision(
    decision_id: int,
    db: Session = Depends(get_db)
):

    discussions = (
        db.query(
            Discussion,
            User
        )
        .join(
            User,
            Discussion.user_id == User.user_id
        )
        .filter(
            Discussion.decision_id == decision_id
        )
        .order_by(
            Discussion.created_at.desc()
        )
        .all()
    )

    result = []

    for discussion, user in discussions:

        result.append({

            "discussion_id": discussion.discussion_id,

            "username": user.username,

            "comment": discussion.comment,

            "discussion_type": discussion.discussion_type,

            "created_at": discussion.created_at

        })

    return result

# ============================================================
# Update Discussion
# ============================================================

@app.put("/discussions/{discussion_id}")
def update_discussion(
    discussion_id: int,
    discussion: DiscussionUpdate,
    db: Session = Depends(get_db)
):

    existing = (
        db.query(Discussion)
        .filter(
            Discussion.discussion_id == discussion_id
        )
        .first()
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Discussion not found."
        )

    # Get user
    user = (
        db.query(User)
        .filter(
            User.user_id == existing.user_id
        )
        .first()
    )

    # Get decision
    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == existing.decision_id
        )
        .first()
    )

    existing.comment = discussion.comment

    try:

        db.commit()

        db.refresh(existing)

        # ============================================================
        # Audit Log
        # ============================================================

        create_audit_log(

            db=db,

            user_id=existing.user_id,

            decision_id=existing.decision_id,

            action_type="Update Discussion",

            description=(
                f'{user.username} updated a discussion '
                f'on decision "{decision.decision_title}".'
            )

        )

    except Exception as e:

        db.rollback()

        raise HTTPException(

            status_code=500,

            detail=f"Could not update discussion: {str(e)}"

        )

    return {

        "message": "Discussion updated successfully."

    }
# ============================================================
# Delete Discussion
# ============================================================

@app.delete("/discussions/{discussion_id}")
def delete_discussion(
    discussion_id: int,
    db: Session = Depends(get_db)
):

    discussion = (
        db.query(Discussion)
        .filter(
            Discussion.discussion_id == discussion_id
        )
        .first()
    )

    if not discussion:
        raise HTTPException(
            status_code=404,
            detail="Discussion not found."
        )

    # Get user
    user = (
        db.query(User)
        .filter(
            User.user_id == discussion.user_id
        )
        .first()
    )

    # Get decision
    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == discussion.decision_id
        )
        .first()
    )

    try:

        user_id = discussion.user_id
        decision_id = discussion.decision_id

        db.delete(discussion)

        db.commit()

        # ============================================================
        # Audit Log
        # ============================================================

        create_audit_log(

            db=db,

            user_id=user_id,

            decision_id=decision_id,

            action_type="Delete Discussion",

            description=(
                f'{user.username} deleted a discussion '
                f'from decision "{decision.decision_title}".'
            )

        )

    except Exception as e:

        db.rollback()

        raise HTTPException(

            status_code=500,

            detail=f"Could not delete discussion: {str(e)}"

        )

    return {

        "message": "Discussion deleted successfully."

    }

# ============================================================
# Create Approval
# ============================================================

@app.post("/approvals", response_model=ApprovalResponse)
def create_approval(
    approval: ApprovalCreate,
    db: Session = Depends(get_db)
):

    new_approval = Approval(

        decision_id=approval.decision_id,

        reviewer_id=approval.reviewer_id,

        approval_level=approval.approval_level,

        status="Pending"

    )

    db.add(new_approval)

    db.commit()

    db.refresh(new_approval)

    return new_approval

# ============================================================
# Get All Approvals
# ============================================================

@app.get("/approvals")
def get_approvals(
    db: Session = Depends(get_db)
):

    approvals = (

        db.query(
            Approval,
            Decision,
            User
        )

        .join(
            Decision,
            Approval.decision_id == Decision.decision_id
        )

        .join(
            User,
            Approval.reviewer_id == User.user_id
        )

        .all()

    )

    result = []

    for approval, decision, reviewer in approvals:

        result.append({

            "id": approval.id,

            "decision_id": decision.decision_id,

            "decision_title": decision.decision_title,

            "reviewer_id": reviewer.user_id,

            "reviewer_name": reviewer.username,

            "approval_level": approval.approval_level,

            "status": approval.status,

            "remarks": approval.remarks,

            "approved_at": approval.approved_at,

            "created_at": approval.created_at

        })

    return result

# ============================================================
# Approval History
# ============================================================

@app.get("/approvals/history")
def get_approval_history(
    db: Session = Depends(get_db)
):

    history = (

        db.query(
            Approval,
            Decision,
            User
        )

        .join(
            Decision,
            Approval.decision_id == Decision.decision_id
        )

        .outerjoin(
            User,
            Approval.reviewer_id == User.user_id
        )

        .order_by(
            Approval.created_at.desc()
        )

        .all()

    )

    result = []

    for approval, decision, user in history:

        result.append({

            "approval_id": approval.id,

            "decision_id": decision.decision_id,

            "decision_title": decision.decision_title,

            "reviewer_name":
                user.username if user else "-",

            "role":
                user.role if user else "-",

            "approval_level":
                approval.approval_level,

            "status":
                approval.status,

            "remarks":
                approval.remarks,

            "created_at":
                approval.created_at,

            "approved_at":
                approval.approved_at

        })

    return result  



# ============================================================
# Get Approvals for a Decision
# ============================================================

@app.get("/decisions/{decision_id}/approvals")
def get_decision_approvals(
    decision_id: int,
    db: Session = Depends(get_db)
):
    decision = (
        db.query(Decision)
        .filter(Decision.decision_id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found."
        )

    approvals = (
        db.query(Approval)
        .filter(Approval.decision_id == decision_id)
        .all()
    )

    return approvals


# ============================================================
# Approve Decision (Reviewer & Manager)
# ============================================================

@app.put("/approvals/{approval_id}/approve")
def approve_decision(
    approval_id: int,
    reviewer_id: int,
    db: Session = Depends(get_db)
):
    # 1. Verify acting user exists
    reviewer = verify_reviewer_manager(reviewer_id, db)

    # 2. Fetch approval record
    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id)
        .first()
    )
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found."
        )

    # 3. Check status
    if approval.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approval already processed. Current status: {approval.status}"
        )

    # 4. Fetch associated decision
    decision = (
        db.query(Decision)
        .filter(Decision.decision_id == approval.decision_id)
        .first()
    )
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found."
        )

    # 5. Prevent self-approval
    if decision.user_id == reviewer.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot approve your own decision."
        )

    # 6. Ensure reviewer is authorized on this specific approval
    if approval.reviewer_id and approval.reviewer_id != reviewer.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to process this specific approval."
        )

    # ==========================================
    # LEVEL 1 : REVIEWER APPROVAL
    # ==========================================
    if approval.approval_level == 1:
        if reviewer.role != "Reviewer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Reviewer can approve Level 1."
            )

        approval.status = "Approved"
        approval.approved_at = datetime.now(timezone.utc)
        decision.status = "Pending Manager Approval"

        # Locate Manager for Level 2
        manager = (
            db.query(User)
            .filter(User.role == "Manager")
            .first()
        )
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manager not found."
            )

        existing = (
            db.query(Approval)
            .filter(
                Approval.decision_id == decision.decision_id,
                Approval.approval_level == 2
            )
            .first()
        )

        if not existing:
            manager_approval = Approval(
                decision_id=decision.decision_id,
                reviewer_id=manager.user_id,
                approval_level=2,
                status="Pending"
            )

            notification = Notification(
                user_id=manager.user_id,
                title="Decision Awaiting Approval",
                message=f'Decision "{decision.decision_title}" is waiting for your approval.',
                type="Approval",
                is_read=False
            )

            db.add(manager_approval)
            db.add(notification)

        # Transactional execution
        try:
            db.commit()

            create_audit_log(
                db=db,
                user_id=reviewer.user_id,
                decision_id=decision.decision_id,
                action_type="Reviewer Approval",
                description=(
                    f'Reviewer "{reviewer.username}" approved '
                    f'decision "{decision.decision_title}".'
                )
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Approval failed: {str(e)}"
            )

        return {
            "message": "Reviewer approved successfully.",
            "status": decision.status
        }

    # ==========================================
    # LEVEL 2 : MANAGER APPROVAL
    # ==========================================
    elif approval.approval_level == 2:
        if reviewer.role != "Manager":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Manager can approve Level 2."
            )

        approval.status = "Approved"
        approval.approved_at = datetime.now(timezone.utc)
        decision.status = "Approved"

        notification = Notification(
            user_id=decision.user_id,
            title="Decision Approved",
            message=f'Your decision "{decision.decision_title}" has been approved.',
            type="Approval",
            is_read=False
        )

        db.add(notification)

        # Transactional execution
        try:
            db.commit()

            create_audit_log(
                db=db,
                user_id=reviewer.user_id,
                decision_id=decision.decision_id,
                action_type="Manager Approval",
                description=(
                    f'Manager "{reviewer.username}" fully approved '
                    f'decision "{decision.decision_title}".'
                )
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Approval failed: {str(e)}"
            )

        return {
            "message": "Decision fully approved.",
            "status": decision.status
        }

    # Fallback for unexpected approval levels
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid approval level."
    )
# ============================================================
# Reject Decision
# ============================================================

@app.put("/approvals/{approval_id}/reject")
def reject_decision(
    approval_id: int,
    reviewer_id: int,
    remarks: str,
    db: Session = Depends(get_db)
):

    reviewer = verify_reviewer_manager(reviewer_id, db)

    approval = (
        db.query(Approval)
        .filter(Approval.id == approval_id)
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval not found."
        )

    decision = (
        db.query(Decision)
        .filter(Decision.decision_id == approval.decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found."
        )

    if decision.user_id == reviewer.user_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot reject your own decision."
        )

    if not remarks or remarks.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Remarks are mandatory."
        )

    approval.status = "Rejected"
    approval.remarks = remarks
    approval.approved_at = datetime.now(timezone.utc)

    decision.status = "Rejected"

    # Notify Decision Owner
    notification = Notification(
        user_id=decision.user_id,
        title="Decision Rejected",
        message=f'Your decision "{decision.decision_title}" was rejected. Remarks: {remarks}',
        type="Approval",
        is_read=False
    )

    try:

        db.add(notification)

        # Save rejection
        db.commit()

        # ============================================================
        # Audit Log
        # ============================================================

        create_audit_log(

            db=db,

            user_id=reviewer.user_id,

            decision_id=decision.decision_id,

            action_type="Reject Decision",

            description=(
                f'{reviewer.role} "{reviewer.username}" rejected '
                f'decision "{decision.decision_title}". '
                f'Remarks: {remarks}'
            )

        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not reject decision: {str(e)}"
        )

    return {

        "message": "Decision rejected successfully.",

        "status": decision.status

    }
# ============================================================
# Verify Reviewer / Manager / Admin
# ============================================================

def verify_reviewer_manager(
    user_id: int,
    db: Session
):
    user = (
        db.query(User)
        .filter(
            User.user_id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    if user.role not in [
        "Reviewer",
        "Manager",
        "Admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Access denied."
        )

    return user


# ============================================================
# Submit Decision Endpoint
# ============================================================

@app.put("/decisions/{decision_id}/submit")
def submit_decision(
    decision_id: int,
    db: Session = Depends(get_db)
):

    # Find Decision
    decision = (
        db.query(Decision)
        .filter(Decision.decision_id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    # Already submitted?
    if decision.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Decision already submitted."
        )

    # Find Reviewer
    reviewer = (
        db.query(User)
        .filter(User.role == "Reviewer")
        .first()
    )

    if not reviewer:
        raise HTTPException(
            status_code=404,
            detail="Reviewer not found."
        )

    # Update Decision Status
    decision.status = "Pending Review"

    # Create Approval Record
    approval = Approval(
        decision_id=decision.decision_id,
        reviewer_id=reviewer.user_id,
        approval_level=1,
        status="Pending"
    )

    # Create Notification
    notification = Notification(
        user_id=reviewer.user_id,
        title="New Decision Submitted",
        message=f'Decision "{decision.decision_title}" requires your approval.',
        type="Approval",
        is_read=False
    )

    try:

        db.add(approval)
        db.add(notification)

        db.commit()

        # ============================================================
        # Audit Log
        # ============================================================

        create_audit_log(

            db=db,

            user_id=decision.user_id,

            decision_id=decision.decision_id,

            action_type="Submit Decision",

            description=(
                f'Decision "{decision.decision_title}" submitted for review.'
            )

        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not submit decision: {str(e)}"
        )

    return {

        "message": "Decision submitted successfully."

    }

# ============================================================
# Approval Details
# ============================================================

@app.get("/approvals/{approval_id}/details")
def get_approval_details(
    approval_id: int,
    db: Session = Depends(get_db)
):

    # ==========================================
    # Approval
    # ==========================================

    approval = (
        db.query(Approval)
        .filter(
            Approval.id == approval_id
        )
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval not found."
        )

    # ==========================================
    # Decision
    # ==========================================

    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == approval.decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found."
        )

    # ==========================================
    # Reviewer
    # ==========================================

    reviewer = (
        db.query(User)
        .filter(
            User.user_id == approval.reviewer_id
        )
        .first()
    )

    # ==========================================
    # Alternatives
    # ==========================================

    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision.decision_id
        )
        .all()
    )

    # ==========================================
    # Criteria
    # ==========================================

    criteria = (
        db.query(Criteria)
        .filter(
            Criteria.decision_id == decision.decision_id
        )
        .all()
    )

    # ==========================================
    # Build Score Matrix & Calculate Totals
    # ==========================================

    score_matrix = []
    alternative_results = []

    for alt in alternatives:

        scores = []
        total_score = 0

        for cri in criteria:

            score = (
                db.query(AlternativeScore)
                .filter(
                    AlternativeScore.alternative_id == alt.alternative_id,
                    AlternativeScore.criteria_id == cri.criteria_id
                )
                .first()
            )

            score_value = score.score if score else 0

            scores.append({

                "criteria_id": cri.criteria_id,

                "criteria_name": cri.criteria_name,

                "score": score_value

            })

            total_score += score_value

        score_matrix.append({

            "alternative_id": alt.alternative_id,

            "alternative_name": alt.alternative_name,

            "scores": scores

        })

        alternative_results.append({

            "alternative_id": alt.alternative_id,

            "alternative_name": alt.alternative_name,

            "estimated_cost": alt.estimated_cost,

            "risk_level": alt.risk_level,

            "feasibility": alt.feasibility,

            "total_score": total_score

        })

    # ==========================================
    # Ranking
    # ==========================================

    alternative_results.sort(
        key=lambda x: x["total_score"],
        reverse=True
    )

    for index, item in enumerate(alternative_results):

        item["rank"] = index + 1

    recommended = (
        alternative_results[0]
        if alternative_results
        else None
    )

    # ==========================================
    # Response
    # ==========================================

    return {

       "approval": {

    "id": approval.id,

    "level": approval.approval_level,

    "status": approval.status

   },

     "reviewer": {

     "id": reviewer.user_id if reviewer else None,

    "name": reviewer.username if reviewer else "",

    "role": reviewer.role if reviewer else ""

   },
        "decision": {

            "id": decision.decision_id,

            "title": decision.decision_title,

            "description": decision.decision_description,

            "status": decision.status

        },

        "recommended_alternative": recommended,

        "alternatives": alternative_results,

        "criteria": [

            {

                "criteria_id": c.criteria_id,

                "name": c.criteria_name,

                "weight": c.weight

            }

            for c in criteria

        ],

        "score_matrix": score_matrix

    }

 # ============================================================
# Get User Notifications
# ============================================================

@app.get("/notifications/{user_id}")
def get_notifications(
    user_id: int,
    db: Session = Depends(get_db)
):

    notifications = (

        db.query(Notification)

        .filter(
            Notification.user_id == user_id
        )

        .order_by(
            Notification.created_at.desc()
        )

        .all()

    )

    return [

        {

            "notification_id": n.notification_id,

            "title": n.title,

            "message": n.message,

            "type": n.type,

            "is_read": n.is_read,

            "created_at": n.created_at

        }

        for n in notifications

    ]

# ============================================================
# Mark Notification as Read
# ============================================================

@app.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):

    notification = (
        db.query(Notification)
        .filter(Notification.notification_id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found."
        )

    notification.is_read = True

    db.commit()

    return {
        "message": "Notification marked as read."
    }

# ============================================================
# Delete Notification
# ============================================================

@app.delete("/notifications/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):

    notification = (
        db.query(Notification)
        .filter(Notification.notification_id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found."
        )

    db.delete(notification)
    db.commit()

    return {
        "message": "Notification deleted."
    }

# ============================================================
# Get Alternatives By Decision
# ============================================================

@app.get("/decisions/{decision_id}/alternatives")
def get_decision_alternatives(
    decision_id: int,
    db: Session = Depends(get_db)
):

    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .all()
    )

    return alternatives

# ============================================================
# Get All Audit Logs
# ============================================================

@app.get(
    "/audit-logs",
    response_model=list[AuditLogResponse]
)
def get_audit_logs(
    db: Session = Depends(get_db)
):

    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    return logs

# ============================================================
# Get Audit Log By ID
# ============================================================

@app.get(
    "/audit-logs/{log_id}",
    response_model=AuditLogResponse
)
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db)
):

    log = (
        db.query(AuditLog)
        .filter(AuditLog.id == log_id)
        .first()
    )

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found."
        )

    return log

# ============================================================
# Get Audit Logs By User
# ============================================================

@app.get(
    "/users/{user_id}/audit-logs",
    response_model=list[AuditLogResponse]
)
def get_user_audit_logs(
    user_id: int,
    db: Session = Depends(get_db)
):

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == user_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    return logs

# ============================================================
# Get Audit Logs By Decision
# ============================================================

@app.get(
    "/decisions/{decision_id}/audit-logs",
    response_model=list[AuditLogResponse]
)
def get_decision_audit_logs(
    decision_id: int,
    db: Session = Depends(get_db)
):

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.decision_id == decision_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    return logs

# ============================================================
# Audit Log Helper
# ============================================================

def create_audit_log(
    db: Session,
    user_id: int,
    action_type: str,
    description: str,
    decision_id: int = None,
    ip_address: str = None
):


    try:

        log = AuditLog(

            user_id=user_id,

            decision_id=decision_id,

            action_type=action_type,

            description=description,

            ip_address=ip_address

        )

        db.add(log)

        db.commit()

        db.refresh(log)

        

        return log

    except Exception as e:

        db.rollback()

        print("AUDIT LOG ERROR:", e)

        raise

# ============================================================
# Reports Dashboard
# ============================================================

from sqlalchemy import func

@app.get("/reports/dashboard")
def reports_dashboard(
    db: Session = Depends(get_db)
):

    return {

        # ==========================
        # Users
        # ==========================

        "total_users":
            db.query(User).count(),

        "admins":
            db.query(User)
            .filter(User.role=="Admin")
            .count(),

        "managers":
            db.query(User)
            .filter(User.role=="Manager")
            .count(),

        "reviewers":
            db.query(User)
            .filter(User.role=="Reviewer")
            .count(),

        "users":
            db.query(User)
            .filter(User.role=="User")
            .count(),

        # ==========================
        # Decisions
        # ==========================

        "total_decisions":
            db.query(Decision).count(),

        "draft":
            db.query(Decision)
            .filter(Decision.status=="Draft")
            .count(),

        "pending_review":
            db.query(Decision)
            .filter(
                Decision.status=="Pending Review"
            )
            .count(),

        "pending_manager":
            db.query(Decision)
            .filter(
                Decision.status=="Pending Manager Approval"
            )
            .count(),

        "approved":
            db.query(Decision)
            .filter(
                Decision.status=="Approved"
            )
            .count(),

        "rejected":
            db.query(Decision)
            .filter(
                Decision.status=="Rejected"
            )
            .count(),

        # ==========================
        # Documents
        # ==========================

        "documents":
            db.query(Document).count(),

        # ==========================
        # Discussions
        # ==========================

        "discussions":
            db.query(Discussion).count(),

        # ==========================
        # Audit Logs
        # ==========================

        "audit_logs":
            db.query(AuditLog).count(),

        # ==========================
        # Approvals
        # ==========================

        "pending_approvals":
            db.query(Approval)
            .filter(
                Approval.status=="Pending"
            )
            .count(),

        "approved_approvals":
            db.query(Approval)
            .filter(
                Approval.status=="Approved"
            )
            .count(),

        "rejected_approvals":
            db.query(Approval)
            .filter(
                Approval.status=="Rejected"
            )
            .count()

    }

# ============================================================
# Get All Audit Logs
# ============================================================

@app.get("/audit-logs")
def get_all_audit_logs(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    if user.role not in ["Admin", "Manager"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied."
        )

    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    return logs

# ============================================================
# KNOWLEDGE REPOSITORY
# ============================================================

@app.get("/knowledge")
def get_knowledge_repository(
    db: Session = Depends(get_db)
):
    """
    Return approved decisions for the Knowledge Repository.
    """

    decisions = (
        db.query(Decision)
        .filter(Decision.status == "Approved")
        .order_by(Decision.created_at.desc())
        .all()
    )

    return decisions

# ============================================================
# Get Knowledge Repository Decision
# ============================================================

@app.get("/knowledge/{decision_id}")
def get_knowledge_decision(
    decision_id: int,
    db: Session = Depends(get_db)
):

    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == decision_id,
            Decision.status == "Approved"
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Approved decision not found."
        )

    return decision

# ============================================================
# PROFESSIONAL DECISION REPORT DATA
# ============================================================

@app.get("/reports/decision/{decision_id}")
def get_decision_report_data(
    decision_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Decision
    # --------------------------------------------------------

    decision = (
        db.query(Decision)
        .filter(
            Decision.decision_id == decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found."
        )

    # --------------------------------------------------------
    # Alternatives
    # --------------------------------------------------------

    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .all()
    )

    # --------------------------------------------------------
    # Criteria
    # --------------------------------------------------------

    criteria = (
        db.query(Criteria)
        .filter(
            Criteria.decision_id == decision_id
        )
        .all()
    )

    # --------------------------------------------------------
    # Scores
    # --------------------------------------------------------

    scores = []

    for alternative in alternatives:

        alternative_scores = (
            db.query(AlternativeScore)
            .filter(
                AlternativeScore.alternative_id
                == alternative.alternative_id
            )
            .all()
        )

        for item in alternative_scores:

            scores.append({
                "alternative_id": item.alternative_id,
                "criteria_id": item.criteria_id,
                "score": item.score
            })

    # --------------------------------------------------------
    # Approvals
    # --------------------------------------------------------

    approvals = (
        db.query(Approval)
        .filter(
            Approval.decision_id == decision_id
        )
        .order_by(
            Approval.created_at.asc()
        )
        .all()
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "decision": {
            "decision_id": decision.decision_id,
            "title": decision.decision_title,
            "description": decision.decision_description,
            "status": decision.status,
            "created_at": decision.created_at
        },

        "alternatives": [

            {
                "alternative_id": item.alternative_id,
                "name": item.alternative_name,
                "description": item.description,
                "pros": item.pros,
                "cons": item.cons,
                "estimated_cost": item.estimated_cost,
                "feasibility": item.feasibility,
                "risk_level": item.risk_level
            }

            for item in alternatives
        ],

        "criteria": [

            {
                "criteria_id": item.criteria_id,
                "name": item.criteria_name,
                "weight": item.weight
            }

            for item in criteria
        ],

        "scores": scores,

        "approvals": [

            {
                "id": item.id,
                "reviewer_id": item.reviewer_id,
                "approval_level": item.approval_level,
                "status": item.status,
                "remarks": item.remarks,
                "approved_at": item.approved_at,
                "created_at": item.created_at
            }

            for item in approvals
        ]
    }