import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Organization, Stats, Event, TeamMember, ContactSubmission

app = FastAPI(title="Hacksters Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# Utility
# ----------------------
class IdModel(BaseModel):
    id: str


def to_serializable(doc):
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d


# ----------------------
# Health & Schema
# ----------------------
@app.get("/")
def read_root():
    return {"message": "Hacksters Portfolio Backend Running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["connection_status"] = "Connected"
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


@app.get("/schema")
def get_schema():
    return {
        "organization": Organization.model_json_schema(),
        "stats": Stats.model_json_schema(),
        "event": Event.model_json_schema(),
        "teammember": TeamMember.model_json_schema(),
        "contactsubmission": ContactSubmission.model_json_schema(),
    }


# ----------------------
# Seed minimal content if empty (optional helper)
# ----------------------
@app.post("/seed")
def seed_minimal():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    created = []
    if db.organization.count_documents({}) == 0:
        created.append(create_document("organization", {
            "name": "HACKSTERS",
            "founded_year": 2019,
            "mission": "Where ideas become reality.",
            "socials": {"github": "https://github.com/", "linkedin": "https://linkedin.com/"}
        }))
    if db.stats.count_documents({}) == 0:
        created.append(create_document("stats", {"patents": 0, "team_size": 8, "achievements": 12}))
    return {"inserted": created}


# ----------------------
# Public GET endpoints
# ----------------------
@app.get("/content/organization")
def get_organization():
    doc = db.organization.find_one({}) if db else None
    return to_serializable(doc) if doc else None


@app.get("/content/stats")
def get_stats():
    doc = db.stats.find_one({}) if db else None
    return to_serializable(doc) if doc else None


@app.get("/timeline", response_model=List[dict])
def list_events():
    docs = get_documents("event") if db else []
    # sort by date descending
    docs_sorted = sorted(docs, key=lambda x: x.get("date", ""), reverse=True)
    return [to_serializable(d) for d in docs_sorted]


@app.get("/team", response_model=List[dict])
def list_team():
    docs = get_documents("teammember") if db else []
    return [to_serializable(d) for d in docs]


# ----------------------
# Admin create endpoints (basic)
# ----------------------
@app.post("/timeline")
def create_event(event: Event):
    inserted_id = create_document("event", event)
    return {"id": inserted_id}


@app.post("/team")
def create_member(member: TeamMember):
    inserted_id = create_document("teammember", member)
    return {"id": inserted_id}


@app.post("/contact")
def submit_contact(data: ContactSubmission):
    inserted_id = create_document("contactsubmission", data)
    return {"id": inserted_id, "status": "received"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
