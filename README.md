# 💳 Expense Tracker with ML Categorisation

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5+-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

An intelligent, full-stack personal finance application that tracks daily expenditures and **automatically categorises transactions using an NLP machine learning pipeline**.

Instead of manually picking categories for every purchase, the embedded Scikit-learn model parses raw merchant text (e.g. *"Uber trip downtown"*, *"Whole Foods Market"*, *"Netflix monthly"*) and predicts the appropriate category in real time.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Machine Learning Engine](#-machine-learning-engine)
  - [Text Representation & Feature Extraction](#text-representation--feature-extraction)
  - [Classification Algorithm](#classification-algorithm)
  - [Active Learning & Continuous Retraining Loop](#active-learning--continuous-retraining-loop)
- [Tech Stack](#-tech-stack)
- [Database Schema](#-database-schema)
- [API Reference](#-api-reference)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [1. Database Setup (Docker)](#1-database-setup-docker)
  - [2. Backend Setup (FastAPI)](#2-backend-setup-fastapi)
  - [3. Frontend Setup (React + Vite)](#3-frontend-setup-react--vite)
- [Multi-Project Port Isolation](#-multi-project-port-isolation)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🚀 Key Features

* **Real-time Predictive Categorisation**: As you type a transaction description, a debounced background hook queries the classifier and displays an instant category badge with a confidence percentage.
* **Auto-Assignment on Submission**: Save transactions without selecting a category—the backend automatically classifies and tags them with an `is_predicted` indicator.
* **Human-in-the-Loop Feedback Loop**: Users can override incorrect predictions in the UI with a single dropdown selection. Corrected entries automatically convert into active training data.
* **On-Demand Model Retraining**: Trigger model retraining directly from the UI (`/retrain`) to update the classifier artifact with recent user corrections.
* **Interactive Data Visualizations**: Real-time spending breakdowns powered by Recharts (Donut/Pie charts and categorical Bar charts).
* **Dockerized Architecture**: Pre-configured `docker-compose.yml` supporting containerized PostgreSQL and multi-project port isolation.

---

## 🏛 System Architecture

```text
┌──────────────────────────────────────────────────────────┐
│                      React 19 Frontend                   │
│   (Transaction Form • Live Debounce • Recharts • Table)  │
└────────────────────────────┬─────────────────────────────┘
                             │ HTTP / JSON (Axios)
                             ▼
┌──────────────────────────────────────────────────────────┐
│                    FastAPI Backend (8001)                │
│  ┌───────────────────────┐    ┌───────────────────────┐  │
│  │   REST API Handlers   │    │ ML Inference Engine   │  │
│  │ (/transactions, etc.) │◄──►│  (Scikit-Learn Model) │  │
│  └───────────┬───────────┘    └───────────▲───────────┘  │
└──────────────┼────────────────────────────┼──────────────┘
               │ SQLAlchemy ORM             │ Retraining
               ▼                            │ (Feedback)
┌───────────────────────────────────────────┴──────────────┐
│                  PostgreSQL Database (5433)              │
│       [categories]  ◄───────────►  [transactions]        │
└──────────────────────────────────────────────────────────┘
```

---

## 🧠 Machine Learning Engine

### Text Representation & Feature Extraction
Bank and credit card transaction descriptions are notoriously noisy, featuring abbreviations, merchant codes, and concatenated strings (e.g., `AMZN*MKTP`, `SWIGGY_BLR_104`, `STARBUCKS #1204`).

Standard word-level tokenization frequently fails on unseen merchant names. To overcome this, the pipeline uses **Character Word-Boundary n-grams (`analyzer="char_wb"`)**:

```python
TfidfVectorizer(
    analyzer="char_wb",
    ngram_range=(2, 4),
    sublinear_tf=True
)
```

* **`ngram_range=(2, 4)`**: Generates character slices of length 2 to 4 within word boundaries. For example, `"uber"` yields `[' u', 'ub', 'be', 'er', 'r ', ' ub', 'ube', 'ber', 'er ']`.
* **Sublinear TF scaling**: Dampens the effect of extremely frequent repetitive terms using logarithmic term frequency:
  $$\text{tf}_{\text{sublinear}} = 1 + \log(\text{tf})$$

### Classification Algorithm
The classifier is built on **Multiclass Logistic Regression** trained using the One-vs-Rest (OvR) scheme with L2 regularization:

```python
Pipeline([
    ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True)),
    ("clf", LogisticRegression(max_iter=2000, C=10))
])
```

* **Confidence Thresholding**: Predictions with maximum posterior probability below `0.25` are left uncategorised rather than making low-confidence false assertions.

### Active Learning & Continuous Retraining Loop

```text
1. User enters: "Lyft airport ride"
   └── Model predicts: "Travel" (is_predicted = True)

2. If prediction is incorrect:
   └── User manually changes category to "Business Expenses"
       └── Database updates: is_predicted = False (verified ground truth)

3. User clicks "Retrain model with my corrections":
   └── System gathers seed samples + all records where (is_predicted == False)
   └── Retrains Scikit-learn Pipeline
   └── Atomically replaces classifier.pkl artifact in memory
```

---

## 🛠 Tech Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+, FastAPI | Async REST API, OpenAPI docs, CORS middleware |
| **ORM & DB Engine** | SQLAlchemy 2.0, Psycopg 3 | Connection pooling, typed DeclarativeBase models |
| **Database** | PostgreSQL 15 | Relational storage running in Docker |
| **Data Validation** | Pydantic v2 | Strict schema validation and serialization |
| **Machine Learning**| Scikit-learn, Joblib | TF-IDF pipeline, Logistic Regression, model serialization |
| **Frontend** | React 19, Vite | Modern component hierarchy, hooks, responsive UI |
| **Data Visualization**| Recharts | Dynamic Pie, Donut, and Bar chart analytics |
| **Containerization** | Docker, Docker Compose | Isolated multi-container environments |

---

## 🗄 Database Schema

```mermaid
erDiagram
    categories ||--o{ transactions : "categorises"
    categories {
        int id PK
        varchar(100) name UK
    }
    transactions {
        int id PK
        date date
        varchar(255) description
        numeric(12,2) amount
        int category_id FK
        boolean is_predicted
        timestamptz created_at
    }
```

* **Indexing Strategy**:
  * `ix_transactions_date` on `transactions.date` for fast monthly queries.
  * `ix_transactions_category_id` on `transactions.category_id` for quick grouping and joins.

---

## 📡 API Reference

### 1. Categories
* **`GET /categories`**: Returns all available expense categories.

### 2. Transactions
* **`GET /transactions`**: Query transactions.
  * Query parameters: `category_id`, `start` (date), `end` (date), `limit`.
* **`POST /transactions`**: Create a transaction.
  ```json
  {
    "date": "2026-11-15",
    "description": "Starbucks cold brew",
    "amount": 5.75,
    "category_id": null
  }
  ```
  *(Leaving `category_id` as `null` invokes the ML predictor automatically).*
* **`PUT /transactions/{tx_id}`**: Update an existing transaction (marks `is_predicted = false`).
* **`DELETE /transactions/{tx_id}`**: Delete a transaction.

### 3. Analytics
* **`GET /summary`**: Aggregates spending totals grouped by category for dashboard charts.

### 4. Machine Learning
* **`POST /predict`**: Real-time prediction endpoint.
  ```json
  // Request
  { "description": "Netflix subscription" }

  // Response
  { "category": "Entertainment", "confidence": 0.942 }
  ```
* **`POST /retrain`**: Merges verified database records with seed samples, retrains the classifier, and reloads the model in-memory.

---

## 💻 Getting Started

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
* Python 3.11+
* Node.js 18+ & npm

---

### 1. Database Setup (Docker)

Start the PostgreSQL database service:

```bash
docker compose up -d db
```
The database runs on port **`5433`** to avoid port collisions with any existing local PostgreSQL instances.

---

### 2. Backend Setup (FastAPI)

1. Open a terminal and navigate to `backend/`:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```powershell
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment variables:
   ```bash
   cp .env.example .env
   ```
5. Pre-train the initial ML classifier model:
   ```bash
   python -m app.ml.train
   ```
6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

* API Docs (Swagger UI): **`http://localhost:8001/docs`**
* Alternative Docs (ReDoc): **`http://localhost:8001/redoc`**

---

### 3. Frontend Setup (React + Vite)

1. Open a second terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
4. Start the Vite development server:
   ```bash
   npm run dev
   ```
5. Open your browser at **`http://localhost:5173`** (or `http://localhost:5174`).

---

## 🔌 Multi-Project Port Isolation

To ensure this project runs seamlessly alongside other developer containers (e.g. `careerops` running on port 8000/5432), default host ports are configured as:

| Service | Container Port | Host Port | Environment Key |
| :--- | :--- | :--- | :--- |
| **PostgreSQL Database** | `5432` | **`5433`** | `DATABASE_URL` in `backend/.env` |
| **FastAPI Backend** | `8000` | **`8001`** | `VITE_API_URL` in `frontend/.env` |
| **React Frontend** | `80` (Docker) / `5173` (Vite) | **`5174`** | — |

---

## 🗺 Roadmap

- [ ] **CSV / Bank Statement Importer**: Bulk file upload supporting OFX, QIF, and standard bank CSV exports.
- [ ] **Transformer-based Embeddings**: Option to toggle between fast local TF-IDF and sentence-transformer embeddings.
- [ ] **Monthly Budget Threshold Alerts**: Visual indicators when category spending exceeds user-defined limits.
- [ ] **Multi-Currency Support**: Exchange rate conversion for international travel expenses.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
