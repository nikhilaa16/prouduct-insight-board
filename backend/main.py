from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os

from database import init_db, get_db, FeedbackItem
from ai_classifier import analyze_feedback

app = FastAPI(title="FeedLoop AI: Customer Experience & Support Analytics API")

# Configure CORS so React frontend can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and vector store
from vector_store import LocalVectorStore
vector_store = LocalVectorStore()

@app.on_event("startup")
def startup_event():
    init_db()
    # Load or rebuild vector index
    if not vector_store.load():
        print("Rebuilding vector database index from database tickets...")
        db = next(get_db())
        try:
            tickets = db.query(FeedbackItem).all()
            vector_store.rebuild_index(tickets)
        except Exception as e:
            print(f"Error rebuilding vector store index: {e}")
        finally:
            db.close()

# Pydantic validation schemas for API inputs
class FeedbackSubmitRequest(BaseModel):
    raw_text: str
    source: Optional[str] = "App Store"
    customer_email: Optional[EmailStr] = None

class StatusUpdateRequest(BaseModel):
    status: str

# API Endpoints

@app.post("/api/feedback/submit")
def submit_feedback(request: FeedbackSubmitRequest, db: Session = Depends(get_db)):
    if not request.raw_text.strip():
        raise HTTPException(status_code=400, detail="Feedback text cannot be empty.")
    
    # 1. Run AI analysis (real or mock simulated)
    analysis = analyze_feedback(request.raw_text)
    
    # 2. Save structured record in database
    db_item = FeedbackItem(
        raw_text=request.raw_text,
        source=request.source,
        customer_email=request.customer_email,
        category=analysis["category"],
        feedback_type=analysis["feedback_type"],
        urgency_score=analysis["urgency_score"],
        ai_summary=analysis["ai_summary"],
        status="New"
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # 3. Add to vector store index
    try:
        metadata = {
            "category": db_item.category,
            "feedback_type": db_item.feedback_type,
            "urgency_score": db_item.urgency_score,
            "status": db_item.status
        }
        vector_store.add_document(db_item.id, db_item.raw_text, metadata)
    except Exception as e:
        print(f"Error adding to vector store: {e}")
        
    return db_item

@app.get("/api/feedback/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(FeedbackItem).count()
    if total == 0:
        return {
            "total_count": 0,
            "bug_count": 0,
            "feature_count": 0,
            "praise_count": 0,
            "average_urgency": 0.0,
            "category_distribution": {},
            "type_distribution": {}
        }
        
    bugs = db.query(FeedbackItem).filter(FeedbackItem.feedback_type == "Bug").count()
    features = db.query(FeedbackItem).filter(FeedbackItem.feedback_type == "Feature Request").count()
    praise = db.query(FeedbackItem).filter(FeedbackItem.feedback_type == "Praise").count()
    
    avg_urgency = db.query(func.avg(FeedbackItem.urgency_score)).scalar() or 0.0
    
    # Category distribution query
    cat_results = db.query(FeedbackItem.category, func.count(FeedbackItem.id)).group_by(FeedbackItem.category).all()
    category_distribution = {cat: count for cat, count in cat_results}
    
    # Type distribution query
    type_results = db.query(FeedbackItem.feedback_type, func.count(FeedbackItem.id)).group_by(FeedbackItem.feedback_type).all()
    type_distribution = {t: count for t, count in type_results}
    
    return {
        "total_count": total,
        "bug_count": bugs,
        "feature_count": features,
        "praise_count": praise,
        "average_urgency": round(float(avg_urgency), 2),
        "category_distribution": category_distribution,
        "type_distribution": type_distribution
    }

@app.get("/api/feedback/list")
def list_feedback(
    category: Optional[str] = None,
    feedback_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(FeedbackItem)
    
    if category:
        query = query.filter(FeedbackItem.category == category)
    if feedback_type:
        query = query.filter(FeedbackItem.feedback_type == feedback_type)
    if status:
        query = query.filter(FeedbackItem.status == status)
        
    # Sort critical items first (highest urgency, newest first)
    return query.order_by(FeedbackItem.urgency_score.desc(), FeedbackItem.created_at.desc()).all()

@app.post("/api/feedback/{item_id}/status")
def update_status(item_id: int, request: StatusUpdateRequest, db: Session = Depends(get_db)):
    db_item = db.query(FeedbackItem).filter(FeedbackItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Feedback item not found.")
    
    valid_statuses = ["New", "Reviewed", "In-Progress", "Resolved"]
    if request.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
        
    db_item.status = request.status
    db.commit()
    db.refresh(db_item)
    return db_item

@app.post("/api/roadmap/generate")
def generate_roadmap(db: Session = Depends(get_db)):
    # Retrieve critical unresolved issues to analyze
    unresolved_bugs = db.query(FeedbackItem).filter(
        FeedbackItem.feedback_type == "Bug",
        FeedbackItem.status != "Resolved"
    ).order_by(FeedbackItem.urgency_score.desc()).all()
    
    if not unresolved_bugs:
        return {
            "roadmap": "### 🎉 Sprint Goal: All Clear!\nNo active, unresolved bugs found. The queue is completely empty. Perfect time to focus on new feature requests!"
        }
        
    # Organize issues into groups for the prompt
    bug_details = []
    for i, bug in enumerate(unresolved_bugs):
        bug_details.append(f"- [{bug.category}] Summary: {bug.ai_summary} (Urgency: {bug.urgency_score}/5)")
        
    # Run the generator
    bug_list_text = "\n".join(bug_details)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            You are a lead technical product manager. Based on this prioritized list of active customer-reported bugs, draft a professional engineering Sprint Planning roadmap in markdown.
            
            Bugs:
            {bug_list_text}
            
            Your response must include:
            1. A concise, catchy Sprint Goal (e.g. 'Sprint Goal: Login Stability and Checkout Fixes').
            2. Priority 1 (Immediate Attention) - issues with urgency 5/5, detailing recommended developer actions.
            3. Priority 2 (Medium Severity) - issues with urgency 4/5 or 3/5.
            4. A short estimated sprint timeline or resource allocation guidance.
            Keep it professional, highly structured, and under 250 words.
            """
            response = model.generate_content(prompt)
            return {"roadmap": response.text}
        except Exception as e:
            print(f"Gemini roadmap call failed, using local template: {e}")
            
    # Local high-quality template fallback
    categories = {}
    for bug in unresolved_bugs:
        categories[bug.category] = categories.get(bug.category, 0) + 1
        
    primary_category = max(categories, key=categories.get)
    
    roadmap_markdown = f"""### 🎯 Sprint Goal: Resolve Critical {primary_category} Issues & Core System Stability

Based on automated classification of {len(unresolved_bugs)} unresolved support tickets, we have generated the following developer action plan:

#### 🚨 Priority 1: Immediate Action (Urgency 5/5)
"""
    
    high_urgency = [b for b in unresolved_bugs if b.urgency_score == 5]
    if high_urgency:
        for b in high_urgency:
            roadmap_markdown += f"- **Fix {b.category} Defect:** *{b.ai_summary}*\n  * Action: Audit server trace, verify input schema, and deploy immediate patch.\n"
    else:
        roadmap_markdown += "- *No Urgency 5/5 issues currently blocking workflows.*\n"
        
    roadmap_markdown += "\n#### ⚡ Priority 2: High/Medium Focus (Urgency 3/5 and 4/5)\n"
    medium_urgency = [b for b in unresolved_bugs if b.urgency_score in [3, 4]]
    for b in medium_urgency[:4]: # Cap at 4 for layout readability
        roadmap_markdown += f"- **Address {b.category} Issue:** *{b.ai_summary}* (Urgency: {b.urgency_score}/5)\n  * Action: Queue for developer triage, add unit testing to prevent regressions.\n"
        
    roadmap_markdown += f"""
#### 📊 Resource Allocation Plan
* **Core Fixes:** 70% of engineering bandwidth allocated to resolve the {len(unresolved_bugs)} active tickets.
* **Testing:** 30% of bandwidth allocated to validating hotfixes on local environments before production releases.
"""
    return {"roadmap": roadmap_markdown}

# Chat Request Schema
class ChatRequest(BaseModel):
    query: str

@app.post("/api/chat")
def chat_with_tickets(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    # 1. Search semantic matches in local vector database
    matches = vector_store.search(request.query, top_k=3)
    
    # 2. Build retrieved context string
    context_texts = []
    for match in matches:
        doc = match["document"]
        score = match["score"]
        context_texts.append(
            f"- [Similarity: {score*100:.1f}%] {doc['text']} "
            f"(Category: {doc['metadata']['category']}, Type: {doc['metadata']['feedback_type']}, Status: {doc['metadata']['status']})"
        )
    context_str = "\n".join(context_texts) if context_texts else "No matching support tickets found."
    
    # 3. Check for Gemini API key to run RAG summary
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            You are a technical support co-pilot. Answer the administrator's query based on the following relevant customer support tickets retrieved from the vector database:
            
            Query: "{request.query}"
            
            Retrieved Context:
            {context_str}
            
            Draft a helpful, concise answer to the query under 100 words. Point out any trends or key items if they are present in the context. If no relevant context is present, state that you couldn't find any relevant support tickets.
            """
            response = model.generate_content(prompt)
            return {
                "answer": response.text.strip(),
                "sources": matches
            }
        except Exception as e:
            print(f"Gemini RAG chat failed, falling back to local: {e}")
            
    # Local fallback structured output
    if not matches:
        answer = "I searched the vector database but couldn't find any relevant customer support tickets matching your query."
    else:
        answer = f"I found {len(matches)} relevant support tickets matching your query. Here is a summary of the matches:\n\n"
        for match in matches:
            doc = match["document"]
            score = match["score"]
            answer += f"• **[{doc['metadata']['category']}]** {doc['text']} (Match: {score*100:.0f}%, Urgency: {doc['metadata']['urgency_score']}/5, Status: {doc['metadata']['status']})\n"
            
    return {
        "answer": answer,
        "sources": matches
    }
