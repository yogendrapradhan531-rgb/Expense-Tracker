/**
 * Axios client configuration and API helper functions for Expense Tracker backend communication.
 */
import axios from "axios";

// Create configured Axios instance pointing to FastAPI backend URL
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8001",
});

// Category endpoints
export const getCategories = () => api.get("/categories").then((r) => r.data);

// Transaction CRUD endpoints
export const getTransactions = (params = {}) =>
  api.get("/transactions", { params }).then((r) => r.data);

export const createTransaction = (data) =>
  api.post("/transactions", data).then((r) => r.data);

export const updateTransaction = (id, data) =>
  api.put(`/transactions/${id}`, data).then((r) => r.data);

export const deleteTransaction = (id) => api.delete(`/transactions/${id}`);

// Analytics summary endpoint for charts
export const getSummary = (params = {}) =>
  api.get("/summary", { params }).then((r) => r.data);

// Real-time ML prediction endpoint
export const predictCategory = (description) =>
  api.post("/predict", { description }).then((r) => r.data);

// Model retraining endpoint incorporating user corrections
export const retrainModel = () => api.post("/retrain").then((r) => r.data);
