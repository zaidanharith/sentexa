import * as XLSX from 'xlsx';

export interface ParsedFileData {
  headers: string[];
  rows: Record<string, unknown>[]; // Mengganti any menjadi unknown
  rowCount: number;
}

export const REQUIRED_COLUMNS = ['ID', 'Ulasan', 'Rating'];

export async function parseFile(file: File): Promise<ParsedFileData> {
  const fileType = file.name.split('.').pop()?.toLowerCase();
  
  if (!['csv', 'xls', 'xlsx'].includes(fileType || '')) {
    throw new Error('Format file harus CSV, XLS, atau XLSX');
  }

  if (fileType === 'csv') {
    return parseCSV(file);
  } else {
    return parseExcel(file);
  }
}

async function parseCSV(file: File): Promise<ParsedFileData> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target?.result as string;
        const lines = text.trim().split('\n');
        if (lines.length === 0) throw new Error('File kosong');

        const headers = lines[0].split(',').map(h => h.trim());
        validateHeaders(headers);

        // Mengganti any menjadi unknown
        const rows: Record<string, unknown>[] = [];
        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(',').map(v => v.trim());
          const row: Record<string, unknown> = {}; // Mengganti any menjadi unknown
          headers.forEach((header, idx) => {
            row[header] = values[idx] || '';
          });
          if (Object.values(row).some(v => v)) {
            rows.push(row);
          }
        }

        resolve({
          headers,
          rows,
          rowCount: rows.length,
        });
      } catch (err) {
        reject(err);
      }
    };
    reader.onerror = () => reject(new Error('Gagal membaca file CSV'));
    reader.readAsText(file);
  });
}

async function parseExcel(file: File): Promise<ParsedFileData> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = e.target?.result as ArrayBuffer;
        const workbook = XLSX.read(data, { type: 'array' });
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
        
        if (!firstSheet) throw new Error('Sheet tidak ditemukan');

        // Menambahkan generic type pada sheet_to_json
        const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(firstSheet);
        if (rows.length === 0) throw new Error('File kosong atau tidak ada data');

        const headers = Object.keys(rows[0]);
        validateHeaders(headers);

        resolve({
          headers,
          rows,
          rowCount: rows.length,
        });
      } catch (err) {
        reject(err);
      }
    };
    reader.onerror = () => reject(new Error('Gagal membaca file Excel'));
    reader.readAsArrayBuffer(file);
  });
}

function validateHeaders(headers: string[]): void {
  const missingColumns = REQUIRED_COLUMNS.filter(
    col => !headers.some(h => h.toUpperCase() === col.toUpperCase())
  );

  if (missingColumns.length > 0) {
    throw new Error(
      `Kolom yang diperlukan hilang: ${missingColumns.join(', ')}\n\nFile harus memiliki kolom: ${REQUIRED_COLUMNS.join(', ')}`
    );
  }
}

export function downloadSampleFile() {
  const sampleData = [
    { ID: '1', Ulasan: 'Produk sangat baik', Rating: '5' },
    { ID: '2', Ulasan: 'Kurang memuaskan', Rating: '2' },
  ];
  
  const ws = XLSX.utils.json_to_sheet(sampleData);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Sample');
  XLSX.writeFile(wb, 'sample_data.xlsx');
}