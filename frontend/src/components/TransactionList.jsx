/**
 * Interactive transactions table allowing inline category corrections and deletions.
 */
import { deleteTransaction, updateTransaction } from "../services/api";

export default function TransactionList({ transactions, categories, onChanged }) {
  // Update transaction category (resets is_predicted flag in database for active learning)
  const changeCategory = async (id, value) => {
    await updateTransaction(id, { category_id: value ? Number(value) : null });
    onChanged();
  };

  // Delete transaction with confirmation
  const remove = async (id) => {
    if (!confirm("Delete this transaction?")) return;
    await deleteTransaction(id);
    onChanged();
  };

  return (
    <div>
      <h2>Transactions</h2>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "2px solid #ddd" }}>
            <th>Date</th>
            <th>Description</th>
            <th>Amount</th>
            <th>Category</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((t) => (
            <tr key={t.id} style={{ borderBottom: "1px solid #eee" }}>
              <td>{t.date}</td>
              <td>{t.description}</td>
              <td>${t.amount.toFixed(2)}</td>
              <td>
                {/* Inline category selector */}
                <select
                  value={t.category_id ?? ""}
                  onChange={(e) => changeCategory(t.id, e.target.value)}
                >
                  <option value="">Uncategorised</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
                {/* Robot badge indicates category was predicted automatically by ML */}
                {t.is_predicted && <span title="Predicted by ML model"> 🤖</span>}
              </td>
              <td>
                <button
                  onClick={() => remove(t.id)}
                  style={{ cursor: "pointer", background: "none", border: "none", color: "#ef4444" }}
                >
                  ✕
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {transactions.length === 0 && <p style={{ color: "#777" }}>No transactions recorded yet.</p>}
    </div>
  );
}
