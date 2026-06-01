# 📊 FeedLoop AI: Customer Experience & Support Analytics Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

**FeedLoop AI** is a full-stack AI/ML administrative intelligence platform that ingests, classifies, and converses with raw, unstructured customer support tickets and review logs. It combines classical machine learning, natural language processing, a custom vector search database (RAG), and generative AI co-pilots in a single dashboard.

---

## 🎨 Premium Theme & UI Design
The admin dashboard is styled with a custom **Zinc / Electric Blue & Sky Glow Premium Palette**, designed to be visually stunning, clean, and distinct:
* **Background:** Deep obsidian dark mode (`#09090B`)
* **Card Material:** Sleek dark card backings (`#18181B`) with subtle borders (`#27272A`)
* **Accent Primary:** High-vibrancy Electric Blue (`#2563EB`)
* **Accent Secondary:** Sky Glow (`#38BDF8`)
* **Alert States:** Emerald Green (`#22C55E` for Praise/Resolved), Amber Orange (`#F59E0B` for Features), and Crimson Red (`#EF4444` for Critical Bugs).

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

## 🛠️ Project Architecture

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
    │   ├── index.css            # Base styles and premium scrollbar coloring
    │   └── main.jsx             # React DOM bootstrapper
    └── vite.config.js           # API proxy routing
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
