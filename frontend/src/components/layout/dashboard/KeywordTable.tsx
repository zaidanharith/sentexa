"use client";

type KeywordItem = {
  word: string;
  count: number;
};

type KeywordTableProps = {
  items: KeywordItem[];
  loading?: boolean;
  emptyLabel: string;
  tone: "positive" | "negative";
  limit?: number;
};

export default function KeywordTable({
  items,
  loading = false,
  emptyLabel,
  tone,
  limit = 5,
}: KeywordTableProps) {
  if (loading) {
    return <p className="text-sm text-gray-500">Memuat...</p>;
  }

  if (!items.length) {
    return <p className="text-sm text-gray-500">{emptyLabel}</p>;
  }

  const isPositive = tone === "positive";
  const borderColor = isPositive ? "border-green-200" : "border-red-200";
  const headerColor = isPositive ? "text-green-700" : "text-red-700";
  const rowHoverColor = isPositive ? "hover:bg-green-50" : "hover:bg-red-50";
  const dotColor = isPositive ? "bg-green-500" : "bg-red-500";
  const badgeColor = isPositive
    ? "bg-green-100 text-green-700"
    : "bg-red-100 text-red-700";

  return (
    <table className="w-full text-sm">
      <thead>
        <tr
          className={`border-b text-lg font-bold ${borderColor} ${headerColor}`}
        >
          <th className="text-left py-2">Kata Kunci</th>
          <th className="text-right py-2">Frekuensi</th>
        </tr>
      </thead>
      <tbody>
        {items.slice(0, limit).map((item, idx) => (
          <tr
            key={`${item.word}-${idx}`}
            className={`border-t ${borderColor} ${rowHoverColor}`}
          >
            <td className="py-2">
              <span className="inline-flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${dotColor}`} />
                <span className="font-medium text-lg">{item.word}</span>
              </span>
            </td>
            <td className="text-right py-2">
              <span
                className={`inline-flex items-center justify-center rounded-full px-3 py-1 text-md font-bold ${badgeColor}`}
              >
                {item.count}x
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
