import { deleteTransaction, updateTransaction } from "../services/api";

export default function TransactionList({ transactions, categories, onChanged }) {
  const changeCategory = async (id, value) => {
    await updateTransaction(id, { category_id: value ? Number(value) : null });
    onChanged();
  };

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
          <tr style={{ textAlign: "left" }}>
            <th>Date</th><th>Description</th><th>Amount</th><th>Category</th><th></th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((t) => (
            <tr key={t.id}>
              <td>{t.date}</td>
              <td>{t.description}</td>
              <td>{t.amount.toFixed(2)}</td>
              <td>
                <select
                  value={t.category_id ?? ""}
                  onChange={(e) => changeCategory(t.id, e.target.value)}
                >
                  <option value="">Uncategorised</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
                {t.is_predicted && <span title="Predicted by ML"> 🤖</span>}
              </td>
              <td><button onClick={() => remove(t.id)}>✕</button></td>
            </tr>
          ))}
        </tbody>
      </table>
      {transactions.length === 0 && <p>No transactions yet.</p>}
    </div>
  );
}