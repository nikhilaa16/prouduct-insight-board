# 📊 FeedLoop AI: Customer Experience & Support Analytics Engine

**FeedLoop AI** is a full-stack administrative operations engine that automatically classifies, prioritizes, and analyzes raw customer support logs. It integrates supervised machine learning, natural language processing, a local vector search database (RAG), and generative AI co-pilots into a single dashboard.

---

## ⚡ Key Features

* **Predictive ML Classifiers:** Employs trained Scikit-Learn pipelines (`TfidfVectorizer` + `LogisticRegression`) to automatically categorize incoming support tickets into categories (`Login`, `Payment`, etc.) and issue types (`Bug`, `Feature Request`, `Praise`).
* **NLP Urgency Mapping:** Uses `TextBlob` sentiment polarity to calculate customer frustration levels and dynamically assign Urgency Scores (1-5).
* **Conversational RAG Co-Pilot:** Includes a semantic chatbot powered by a local, pure-Python vector database (`vector_store.py`) and Cosine Similarity to search logs and generate grounded summaries with source citations.
* **AI Sprint Planner:** Generates structured engineering sprint roadmaps from unresolved defects using Gemini (or a smart local fallback).
* **Full-Stack Dashboard:** A React dashboard (Vite + Tailwind CSS + Recharts) connected to a FastAPI backend and PostgreSQL database.

---

## 🛠️ Project Directory Structure

```text
feedloop-insight-board/
├── backend/
│   ├── models/                  # Serialized ML model pipelines (.pkl)
│   ├── database.py              # PostgreSQL database & SQLAlchemy ORM mapping
│   ├── ai_classifier.py         # Model loader & TextBlob sentiment Urgency scoring
│   ├── vector_store.py          # Custom local vector database & Cosine Similarity search
│   ├── train_model.py           # Offline Scikit-Learn classifier training pipeline
│   ├── main.py                  # FastAPI REST API endpoints
│   ├── requirements.txt         # Backend Python dependencies
│   └── test_api.py              # E2E API test script
└── frontend/
    ├── src/
    │   ├── App.jsx              # React dashboard, charts, & RAG chat co-pilot
    │   ├── index.css            # Base styles and custom scrollbar tracks
    │   └── main.jsx             # React DOM bootstrapper
    ├── vite.config.js           # Proxy configuration mapping /api to port 8000
    └── package.json             # Frontend script triggers
```

---

## 🚀 Getting Started

### 1. Backend Setup & Model Training
Configure your PostgreSQL connection settings in `backend/database.py` if needed.

```bash
# Navigate to the backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Train local ML models (Required before starting server)
python train_model.py

# Start the FastAPI server
uvicorn main:app --reload
```
* Interactive Swagger API documentation will run at: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup & Run
```bash
# Navigate to the frontend directory
cd ../frontend

# Install node dependencies
npm install

# Run the React client in dev mode
npm run dev
```
* Open your browser and navigate to: `http://localhost:5173/`

### 3. Verification Testing
Verify that all ML and RAG chat endpoints are functional:
```bash
cd backend
python test_api.py
```
