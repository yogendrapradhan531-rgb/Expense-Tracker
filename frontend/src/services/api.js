import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export const getCategories = () => api.get("/categories").then((r) => r.data);
export const getTransactions = (params = {}) =>
  api.get("/transactions", { params }).then((r) => r.data);
export const createTransaction = (data) =>
  api.post("/transactions", data).then((r) => r.data);
export const updateTransaction = (id, data) =>
  api.put(`/transactions/${id}`, data).then((r) => r.data);
export const deleteTransaction = (id) => api.delete(`/transactions/${id}`);
export const getSummary = (params = {}) =>
  api.get("/summary", { params }).then((r) => r.data);
export const predictCategory = (description) =>
  api.post("/predict", { description }).then((r) => r.data);
export const retrainModel = () => api.post("/retrain").then((r) => r.data);