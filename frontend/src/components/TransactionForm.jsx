/**
 * Transaction creation form featuring real-time debounced NLP category predictions.
 */
import { useEffect, useState } from "react";
import { createTransaction, predictCategory } from "../services/api";

const today = () => new Date().toISOString().slice(0, 10);

export default function TransactionForm({ categories, onCreated }) {
  const [form, setForm] = useState({
    date: today(),
    description: "",
    amount: "",
    category_id: "", // Empty string means "auto-detect via ML"
  });
  const [suggestion, setSuggestion] = useState(null);
  const [error, setError] = useState("");

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  // Live debounced ML category suggestion as the user types a description
  useEffect(() => {
    if (form.description.trim().length < 3) {
      setSuggestion(null);
      return;
    }
    const timer = setTimeout(() => {
      predictCategory(form.description)
        .then(setSuggestion)
        .catch(() => {});
    }, 400);
    return () => clearTimeout(timer);
  }, [form.description]);

  // Form submission handler
  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await createTransaction({
        date: form.date,
        description: form.description.trim(),
        amount: parseFloat(form.amount),
        category_id: form.category_id ? Number(form.category_id) : null,
      });
      // Reset form state on successful submission
      setForm({ ...form, description: "", amount: "", category_id: "" });
      setSuggestion(null);
      onCreated();
    } catch (err) {
      setError(err.response?.data?.detail?.[0]?.msg || "Could not save transaction");
    }
  };

  return (
    <form onSubmit={submit} style={{ display: "grid", gap: 8, maxWidth: 420 }}>
      <h2>Add transaction</h2>

      <label>
        Date:
        <input type="date" value={form.date} onChange={set("date")} required />
      </label>

      <label>
        Description:
        <input
          type="text"
          placeholder="e.g. Starbucks coffee, Uber ride"
          value={form.description}
          onChange={set("description")}
          required
        />
      </label>

      {/* Real-time category prediction badge */}
      {suggestion?.category && !form.category_id && (
        <div style={{ fontSize: 13, color: "#4f46e5", background: "#eef2ff", padding: "4px 8px", borderRadius: 4 }}>
          ✨ Suggested category: <strong>{suggestion.category}</strong> ({(suggestion.confidence * 100).toFixed(0)}% confidence)
        </div>
      )}

      <label>
        Amount:
        <input
          type="number"
          step="0.01"
          placeholder="0.00"
          value={form.amount}
          onChange={set("amount")}
          required
        />
      </label>

      <label>
        Category:
        <select value={form.category_id} onChange={set("category_id")}>
          <option value="">Auto-detect with ML</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </label>

      {error && <p style={{ color: "#ef4444" }}>{error}</p>}

      <button type="submit" style={{ padding: 8, cursor: "pointer" }}>Save Transaction</button>
    </form>
  );
}
