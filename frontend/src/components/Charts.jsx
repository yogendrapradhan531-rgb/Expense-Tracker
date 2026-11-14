/**
 * Visual breakdown of expenses by category using Recharts (Pie and Bar charts).
 */
import { Bar, BarChart, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

// Consistent palette for visual distinction across categories
const COLORS = [
  "#4f46e5", "#16a34a", "#f59e0b", "#ef4444",
  "#06b6d4", "#a855f7", "#64748b", "#ec4899"
];

export default function Charts({ summary }) {
  if (!summary.length) return null;

  // Format data payload for Recharts components
  const data = summary.map((s) => ({ name: s.category, value: s.total }));

  return (
    <div>
      <h2>Spending by Category</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 24 }}>
        {/* Pie chart showing relative category distribution */}
        <ResponsiveContainer width={360} height={280}>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" outerRadius={100} label>
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(val) => `$${Number(val).toFixed(2)}`} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>

        {/* Bar chart showing absolute dollar spend per category */}
        <ResponsiveContainer width={420} height={280}>
          <BarChart data={data}>
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis />
            <Tooltip formatter={(val) => `$${Number(val).toFixed(2)}`} />
            <Bar dataKey="value" fill="#4f46e5" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
