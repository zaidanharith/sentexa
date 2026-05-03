'use client';

import { ParsedFileData } from '@/lib/file-parser';

interface DataPreviewProps {
  data: ParsedFileData;
  maxRows?: number;
}

export function DataPreview({ data, maxRows = 5 }: DataPreviewProps) {
  const displayedRows = data.rows.slice(0, maxRows);
  const hasMoreRows = data.rows.length > maxRows;

  return (
    <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              {data.headers.map((header) => (
                <th
                  key={header}
                  className="px-4 py-3 text-left font-semibold text-gray-900"
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {displayedRows.map((row, idx) => (
              <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                {data.headers.map((header) => (
                  <td key={`${idx}-${header}`} className="px-4 py-3 text-gray-700">
                    {String(row[header] || '-')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {hasMoreRows && (
        <div className="px-4 py-3 bg-gray-50 text-sm text-gray-600 border-t border-gray-200">
          Menampilkan {displayedRows.length} dari {data.rows.length} data
        </div>
      )}
    </div>
  );
}