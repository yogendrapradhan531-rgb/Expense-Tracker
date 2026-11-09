import { Bar, BarChart, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const COLORS = ["#4f46e5", "#16a34a", "#f59e0b", "#ef4444", "#06b6d4", "#a855f7", "#64748b", "#ec4899"];

export default function Charts({ summary }) {
  if (!summary.length) return null;
  const data = summary.map((s) => ({ name: s.category, value: s.total }));

  return (
    <div>
      <h2>Spending by category</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 24 }}>
        <ResponsiveContainer width={360} height={280}>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" outerRadius={100}>
              {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
        <ResponsiveContainer width={420} height={280}>
          <BarChart data={data}>
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#4f46e5" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}