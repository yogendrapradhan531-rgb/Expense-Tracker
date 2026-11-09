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

  const refresh = useCallback(async () => {
    const [tx, sm] = await Promise.all([getTransactions(), getSummary()]);
    setTransactions(tx);
    setSummary(sm);
  }, []);

  useEffect(() => {
    getCategories().then(setCategories);
    refresh();
  }, [refresh]);

  const retrain = async () => {
    const { trained_on } = await retrainModel();
    setMsg(`Model retrained on ${trained_on} samples`);
    setTimeout(() => setMsg(""), 4000);
  };

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: 24, fontFamily: "system-ui" }}>
      <h1>Expense Tracker</h1>
      <TransactionForm categories={categories} onCreated={refresh} />
      <hr style={{ margin: "24px 0" }} />
      <Charts summary={summary} />
      <hr style={{ margin: "24px 0" }} />
      <TransactionList transactions={transactions} categories={categories} onChanged={refresh} />
      <hr style={{ margin: "24px 0" }} />
      <button onClick={retrain}>Retrain model with my corrections</button>
      {msg && <span style={{ marginLeft: 12 }}>{msg}</span>}
    </div>
  );
}