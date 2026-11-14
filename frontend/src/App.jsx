/**
 * Main application dashboard integrating Transaction Form, Charts, and Transaction Table.
 */
import { useCallback, useEffect, useState } from "react";
import Charts from "./components/Charts";
import TransactionForm from "./components/TransactionForm";
import TransactionList from "./components/TransactionList";
import { getCategories, getSummary, getTransactions, retrainModel } from "./services/api";

export default function App() {
  const [categories, setCategories] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState([]);
  const [msg, setMsg] = useState("");

  // Refresh transactions list and category summary totals
  const refresh = useCallback(async () => {
    const [tx, sm] = await Promise.all([getTransactions(), getSummary()]);
    setTransactions(tx);
    setSummary(sm);
  }, []);

  // Fetch initial data on mount
  useEffect(() => {
    getCategories().then(setCategories);
    refresh();
  }, [refresh]);

  // Trigger server-side model retraining with user corrections
  const retrain = async () => {
    const { trained_on } = await retrainModel();
    setMsg(`Model successfully retrained on ${trained_on} samples`);
    setTimeout(() => setMsg(""), 4000);
  };

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: 24, fontFamily: "system-ui" }}>
      <h1>Expense Tracker with ML Categorisation</h1>
      <p style={{ color: "#666" }}>
        Transactions are automatically categorised using an NLP model trained on description text.
      </p>

      {/* Transaction Entry Form with Real-time ML Prediction */}
      <TransactionForm categories={categories} onCreated={refresh} />
      
      <hr style={{ margin: "24px 0" }} />
      
      {/* Category Spending Breakdown Visualizations */}
      <Charts summary={summary} />
      
      <hr style={{ margin: "24px 0" }} />
      
      {/* Interactive Transactions Table with Category Overrides */}
      <TransactionList transactions={transactions} categories={categories} onChanged={refresh} />
      
      <hr style={{ margin: "24px 0" }} />
      
      {/* Continuous Learning Retrain Trigger */}
      <button onClick={retrain} style={{ padding: "8px 16px", cursor: "pointer" }}>
        Retrain model with my corrections
      </button>
      {msg && <span style={{ marginLeft: 12, color: "#16a34a", fontWeight: "bold" }}>{msg}</span>}
    </div>
  );
}
