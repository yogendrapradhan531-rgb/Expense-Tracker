# Expense Tracker with ML Categorisation

A full-stack expense tracking web application that automatically categorises expenses from transaction descriptions using Natural Language Processing (NLP).

Built with **FastAPI**, **React**, **PostgreSQL**, and **Scikit-learn**.

---

## Features

- **Automated ML Categorisation**: Predicts spending categories (Food, Groceries, Utilities, Travel, Shopping, Healthcare, Entertainment) using a TF-IDF + Logistic Regression NLP pipeline.
- **Real-time Live Suggestions**: Debounced category suggestions appear dynamically as you type transaction descriptions.
- **Continuous Learning Loop**: Manual corrections made in the UI update transaction labels and feed back into the model when retraining.
- **Visual Analytics**: Interactive category distribution charts using Recharts (Pie & Bar charts).
- **Docker Compose Setup**: Containerized PostgreSQL database and services with customizable port bindings.

---

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Uvicorn, Pydantic v2
- **Machine Learning**: Scikit-Learn (TF-IDF Vectorizer with character n-grams + Logistic Regression), Joblib
- **Database**: PostgreSQL 15 (Docker)
- **Frontend**: React 19, Vite, Recharts, Axios

---

## Getting Started

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.11+
- Node.js 18+

### 2. Database Setup
Start the PostgreSQL container:
```bash
docker compose up -d db
```
*(Runs on host port `5433` by default to avoid conflicts).*

### 3. Backend Setup
1. Create and activate a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
4. Train the initial ML model artifact:
   ```bash
   python -m app.ml.train
   ```
5. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```
   API Swagger docs will be available at: `http://localhost:8001/docs`

### 4. Frontend Setup
1. In a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install packages:
   ```bash
   npm install
   ```
3. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
4. Start the Vite dev server:
   ```bash
   npm run dev
   ```
   Open your browser at `http://localhost:5173` (or `http://localhost:5174`).

---

## Project Structure

```text
expense-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application & route handlers
│   │   ├── database.py          # SQLAlchemy connection & session manager
│   │   ├── models.py            # Database models (Category, Transaction)
│   │   ├── schemas.py           # Pydantic request/response validation schemas
│   │   └── ml/
│   │       ├── train.py         # NLP training pipeline & sample data
│   │       ├── predict.py       # Inference & prediction utility
│   │       └── classifier.pkl   # Serialized model artifact
│   ├── requirements.txt         # Python dependencies
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Charts.jsx          # Recharts visualizations
│   │   │   ├── TransactionForm.jsx # Entry form with live prediction
│   │   │   └── TransactionList.jsx # Table with inline corrections
│   │   ├── services/
│   │   │   └── api.js              # Axios backend client
│   │   ├── App.jsx                 # Main dashboard component
│   │   └── main.jsx
│   ├── package.json
│   └── .env.example
├── docker-compose.yml           # Container orchestration
└── README.md
```
