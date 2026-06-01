# 📊 FeedLoop AI: Customer Experience & Support Analytics Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

**FeedLoop AI** is a full-stack administrative operations engine that automates the audit, classification, and analysis of raw customer support logs and review texts. It combines traditional machine learning, natural language processing, a custom local vector database (RAG), and generative AI co-pilots in a single React administrative dashboard.

---

## ⚡ Core AI/ML Features

### 🧠 1. Predictive ML Classifiers (Pillar 1)
Instead of basic keyword matching, FeedLoop utilizes custom-trained machine learning pipelines to predict metadata from raw text:
* **Category Classifier:** Classifies logs into `Login`, `Payment`, `UI/UX`, `Performance`, or `Others`.
* **Issue Type Classifier:** Classifies logs into `Bug`, `Feature Request`, or `Praise`.
* **Tech Stack:** Scikit-Learn `TfidfVectorizer` (feature extraction) + `LogisticRegression` (supervised classification). Models are serialized locally via `joblib`.

### 📈 2. NLP Sentiment-Based Urgency Mapping (Pillar 1)
* Automatically determines customer frustration levels using **TextBlob NLP Sentiment Polarity**.
* Maps negative polarity to elevated **Urgency Scores (1 to 5)**.
* Utilizes a hybrid model-rule backup to immediately flag critical operational keywords (e.g. `crashes`, `broken`, `billing failed`).

### 💬 3. Conversational RAG Search Engine (Pillar 2)
* Includes a built-in semantic chatbot letting administrators chat with ticket databases in natural language.
* Uses a **custom, pure-Python local Vector Database (`vector_store.py`)** that calculates **Cosine Similarity** to index and retrieve matching sources (no complex C++ compilation or cloud costs).
* Combines matching sources as grounded context for a generated co-pilot response, complete with citation badges showing similarity scores.

### 🤖 4. AI Sprint Co-Pilot (Pillar 3)
* Groups unresolved database tickets and generates structured, professional **Engineering Sprint Plans** and timeline recommendations using Gemini (or a smart local markdown fallback).

---

## 📋 API Endpoints Reference

| HTTP Method | Route | Description | Request Payload | Response Schema |
| :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/feedback/submit` | Analyzes and ingests a raw support log into the database and vector store. | `{"raw_text": str, "source": str, "customer_email": str}` | Ingested `FeedbackItem` object with category/type predictions. |
| **GET** | `/api/feedback/stats` | Fetches aggregated statistics, average urgency scores, and distribution counts. | *None* | `{"total_count": int, "bug_count": int, "category_distribution": dict, ...}` |
| **GET** | `/api/feedback/list` | Returns sorted support tickets. Supports filtering by category, type, and status. | Query parameters: `?category=x&feedback_type=y&status=z` | Array of `FeedbackItem` objects sorted by urgency score. |
| **POST** | `/api/feedback/{id}/status` | Updates the status of a specific ticket (New, Reviewed, In-Progress, Resolved). | `{"status": str}` | Updated `FeedbackItem` object. |
| **POST** | `/api/roadmap/generate` | Generates a prioritized engineering sprint roadmap from unresolved defects. | *None* | `{"roadmap": "markdown string"}` |
| **POST** | `/api/chat` | Performs semantic vector search on ticket logs and generates summarized replies. | `{"query": str}` | `{"answer": str, "sources": [{"document": dict, "score": float}]}` |
| **POST** | `/api/feedback/clear` | Wipes the entire database table and resets the local vector index. | *None* | `{"detail": str}` |

---

## 🗄️ Database Schema Structure

All tickets are written to your local PostgreSQL instance under the table `feedback_items`:

| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | Primary Key, Indexed | Auto-incrementing identifier. |
| `raw_text` | `Text` | Not Null | Original support text or review log. |
| `source` | `String(50)` | Default: `'App Store'` | Ingestion source (iOS App, Play Store, etc.). |
| `customer_email`| `String(100)`| Nullable | Submitter contact details. |
| `category` | `String(50)` | Default: `'Others'` | ML Predicted: `Login`, `Payment`, `UI/UX`, `Performance`, `Others`. |
| `feedback_type` | `String(50)` | Default: `'Bug'` | ML Predicted: `Bug`, `Feature Request`, `Praise`. |
| `urgency_score` | `Integer` | Default: `1` | Predictive NLP rating from `1` (lowest) to `5` (highest). |
| `ai_summary` | `String(255)`| Nullable | Concise AI trimer (under 10 words). |
| `status` | `String(50)` | Default: `'New'` | Ticket state: `New`, `Reviewed`, `In-Progress`, `Resolved`. |
| `created_at` | `DateTime` | Default: `utcnow` | Server-side ingestion timestamp. |

---

## 🧠 Local AI/ML Workflow

### 1. Classification Training Pipeline (`train_model.py`)
- Standardizes text features using **TF-IDF Term Frequency Vectorization** with n-grams `(1, 2)`.
- Fits two independent supervised **Logistic Regression** classifiers.
- Serializes pipeline weights using `joblib` into `backend/models/`.

### 2. Conversational RAG Engine (`vector_store.py`)
```text
[User Chat Query] 
       │
       ▼
 [Vectorization]  ──► [TF-IDF Feature Mapping]
       │
       ▼
 [Cosine Similarity Index] ──► Compare query coordinates against database logs
       │
       ▼
 [Top K Retrieval]  ──► Grabs matches with highest match score percentages
       │
       ▼
 [Generative Answer] ──► Summarizes context and returns sources to UI
```

---

## 🛠️ Project Directory Tree

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

### Prerequisites
* **Python 3.13+**
* **Node.js 18+**
* Running instance of **PostgreSQL** (with database `feedloop_db` created).

### 1. Backend Setup & Model Training
```bash
# Navigate to the backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# 1. TRAIN LOCAL ML MODELS (Required before starting server)
python train_model.py

# 2. Start the FastAPI server
uvicorn main:app --reload
```
* Swagger API documentation: `http://127.0.0.1:8000/docs`

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

### 3. Production Build
To bundle the frontend for production:
```bash
npm run build
```

---

## 🧪 Automated Verification Testing

Verify all systems (Ingestion predictions, stats, roadmap planner, and Conversational RAG queries) are functional by running:
```bash
cd backend
python test_api.py
```
