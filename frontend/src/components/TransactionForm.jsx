import { useEffect, useState } from "react";
import { createTransaction, predictCategory } from "../services/api";

const today = () => new Date().toISOString().slice(0, 10);

export default function TransactionForm({ categories, onCreated }) {
  const [form, setForm] = useState({
    date: today(),
    description: "",
    amount: "",
    category_id: "", // "" = auto-detect with ML
  });
  const [suggestion, setSuggestion] = useState(null);
  const [error, setError] = useState("");

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  // Live suggestion while typing (debounced)
  useEffect(() => {
    if (form.description.trim().length < 3) {
      setSuggestion(null);
      return;
    }
    const t = setTimeout(() => {
      predictCategory(form.description).then(setSuggestion).catch(() => {});
    }, 400);
    return () => clearTimeout(t);
  }, [form.description]);

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
      <input type="date" value={form.date} onChange={set("date")} required />
      <input
        placeholder="Description (e.g. Starbucks Coffee downtown)"
        value={form.description}
        onChange={set("description")}
        required
      />
      <input
        type="number"
        step="0.01"
        min="0.01"
        placeholder="Amount"
        value={form.amount}
        onChange={set("amount")}
        required
      />
      <select value={form.category_id} onChange={set("category_id")}>
        <option value="">Auto-detect (ML)</option>
        {categories.map((c) => (
          <option key={c.id} value={c.id}>{c.name}</option>
        ))}
      </select>
      {suggestion?.category && !form.category_id && (
        <small>
          Suggested: <b>{suggestion.category}</b> ({Math.round(suggestion.confidence * 100)}%)
        </small>
      )}
      {error && <small style={{ color: "crimson" }}>{error}</small>}
      <button type="submit">Add</button>
    </form>
  );
}