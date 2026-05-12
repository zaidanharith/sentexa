"use client";

import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from "recharts";

type DonutChartProps = {
  positivePercent: number;
  negativePercent: number;
  neutralPercent: number;
  loading?: boolean;
};

const COLORS = {
  positive: "#22c55e",
  negative: "#ef4444",
  neutral: "#94a3b8",
};

const CustomTooltip = ({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; payload: { name: string } }>;
}) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-2 rounded shadow-lg border border-gray-200">
        <p className="text-sm font-semibold">{payload[0].payload.name}</p>
        <p className="text-sm">{payload[0].value}%</p>
      </div>
    );
  }
  return null;
};

export default function DonutChart({
  positivePercent,
  negativePercent,
  neutralPercent,
  loading = false,
}: DonutChartProps) {
  if (loading) {
    return <p className="text-sm text-gray-500">Memuat...</p>;
  }

  const data = [
    {
      name: "Positif",
      value: positivePercent,
      fill: COLORS.positive,
    },
    {
      name: "Negatif",
      value: negativePercent,
      fill: COLORS.negative,
    },
    {
      name: "Netral",
      value: neutralPercent,
      fill: COLORS.neutral,
    },
  ];

  // Filter out zero values for better visualization
  const filteredData = data.filter((item) => item.value > 0);

  if (filteredData.length === 0) {
    return <p className="text-sm text-gray-500">Belum ada data sentimen</p>;
  }

  return (
    <div className="h-80 w-full flex flex-col items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={filteredData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="value"
            label={({ name, value }) => `${name} ${value}%`}
          >
            {filteredData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value) => value}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}