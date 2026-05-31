# 📊 FeedLoop AI: Customer Experience & Support Analytics Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)

**FeedLoop AI** is a state-of-the-art administrative intelligence engine designed to automatically audit, classify, and prioritize raw customer feedback, reviews, and support logs. By parsing user feedback, it extracts categories, issue types, and urgency scores to empower engineering and product teams with structured, actionable insights.

---

## 🎨 Premium Theme & UI Design
The admin dashboard is styled using a custom **Zinc / Electric Blue & Sky Glow Premium Palette**, designed to be visually stunning, clean, and completely distinct from standard templates:
* **Background:** Deep obsidian dark mode (`#09090B`)
* **Card Material:** Sleek dark card backings (`#18181B`) with subtle borders (`#27272A`)
* **Accent Primary:** High-vibrancy Electric Blue (`#2563EB`)
* **Accent Secondary:** Sky Glow (`#38BDF8`)
* **Alert States:** Emerald Green (`#22C55E` for Praise/Resolved), Amber Orange (`#F59E0B` for Features), and Crimson Red (`#EF4444` for Critical Bugs).

---

## ⚡ Core Features

* 📥 **Support Ticket Ingestion:** Ingest raw customer messages from the App Store, Play Store, Web Portal, iOS App, or Email Support.
* 🧠 **AI Classification & Classification Engine:** Automatically tags issues as **Bug**, **Feature Request**, or **Praise**, maps them to categories (**Login**, **Payment**, **UI/UX**, **Performance**, or **Others**), and assigns a strict **Urgency Score (1 to 5)**.
* 📊 **Interactive Analytics Board:** Real-time graphs powered by **Recharts** detailing **Category Load** (bar charts with custom tooltips) and **Issue Mix** (donut chart distribution).
* 📋 **Live Ticket Queue:** Powerful filtering by category, issue type, and search queries with inline status changes (New, Reviewed, In-Progress, Resolved) backed directly by SQL transaction writes.
* 🤖 **AI Sprint Co-Pilot:** Compiles unresolved defects and feature requests into prioritized engineering sprint roadmaps instantly.

---

## 🛠️ Tech Stack & Architecture

```text
feedloop-insight-board/
├── backend/
│   ├── database.py              # PostgreSQL SQLAlchemy ORM configurations
│   ├── ai_classifier.py         # AI extraction & simulation pipeline
│   ├── main.py                  # FastAPI REST API layer
│   ├── requirements.txt         # Backend python packages
│   └── test_api.py              # End-to-end API test script
└── frontend/
    ├── src/
    │   ├── App.jsx              # React dashboard container & custom theme variables
    │   ├── index.css            # Custom base scrollbars and typography
    │   └── main.jsx             # React client entry point
    ├── vite.config.js           # Proxy configuration mapping /api to port 8000
    └── package.json             # Frontend script triggers
```

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.13+**
* **Node.js 18+**
* Running instance of **PostgreSQL** (with a database named `feedloop_db` created).

### 1. Backend Setup & Run
Configure your PostgreSQL connection parameters in `backend/database.py` (defaults to local connection details).

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI Server
uvicorn main:app --reload
```
* Swagger interactive docs will be available at: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup & Run
The frontend is built on React + Vite and proxies requests to the FastAPI backend.

```bash
# Navigate to the frontend directory
cd ../frontend

# Install dependencies
npm install

# Run Vite in development mode
npm run dev
```
* Open your browser and navigate to: `http://localhost:5173/`

### 3. Production Build
To bundle the frontend for production:
```bash
npm run build
```
This builds optimized HTML, CSS, and JS chunks into the `frontend/dist` directory.

---

## 🧪 Automated Testing

We have built a dedicated integration test suite to verify the database connectivity, API request lifecycle, and schema validation. Run it using:
```bash
cd backend
python test_api.py
```

---

## 📄 License
This project is licensed under the MIT License. Developed for customer success engineering.
