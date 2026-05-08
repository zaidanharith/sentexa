"use client";

import {
  Line,
  LineChart,
  CartesianGrid,
  Tooltip,
  XAxis,
  YAxis,
  ResponsiveContainer,
} from "recharts";

type TrendItem = {
  date: string;
  positive: number;
  negative: number;
};

type TrendChartProps = {
  data: TrendItem[];
  loading?: boolean;
};

const formatDate = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleDateString("id-ID", {
    day: "2-digit",
    month: "short",
  });
};

export default function TrendChart({ data, loading = false }: TrendChartProps) {
  if (loading) {
    return <p className="text-sm text-gray-500">Memuat...</p>;
  }

  if (!data.length) {
    return <p className="text-sm text-gray-500">Belum ada data tren</p>;
  }

  return (
    <div className="h-60 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 10, right: 12, left: -12, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            tick={{ fontSize: 12, fill: "#64748b" }}
            axisLine={{ stroke: "#e2e8f0" }}
            tickLine={{ stroke: "#e2e8f0" }}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "#64748b" }}
            axisLine={{ stroke: "#e2e8f0" }}
            tickLine={{ stroke: "#e2e8f0" }}
            allowDecimals={false}
          />
          <Tooltip
            labelFormatter={(label) => `Tanggal ${formatDate(String(label))}`}
            formatter={(value, name) => [
              value,
              name === "positive" ? "Positif" : "Negatif",
            ]}
          />
          <Line
            type="monotone"
            dataKey="positive"
            stroke="#22c55e"
            strokeWidth={4}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            name="positive"
          />
          <Line
            type="monotone"
            dataKey="negative"
            stroke="#ef4444"
            strokeWidth={4}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            name="negative"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
