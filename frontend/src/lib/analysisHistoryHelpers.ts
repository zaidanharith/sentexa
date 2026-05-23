export type AnalysisPrediction = {
  label?: string;
  score?: number | null;
  scores?: Record<string, number> | null;
};

export type AnalysisHistoryItem = {
  id: number;
  source_type: string;
  input_text: string | null;
  result_label: string | null;
  result_score: number | null;
  result_payload: AnalysisPrediction[] | Record<string, unknown> | null;
  status: string;
  created_at: string;
};

export type AnalysisHistoryResponse = {
  items: AnalysisHistoryItem[];
  count: number;
};

export type SentimentJobItem = {
  job_id: string;
  status: string;
  total_texts: number;
  completed_count: number;
  label_counts?: Record<string, number>;
  created_at: string;
  updated_at: string;
  error?: string | null;
};

export function formatLabel(label: string | null): string {
  if (!label) {
    return "-";
  }
  return label.charAt(0).toUpperCase() + label.slice(1);
}

export function formatScore(score?: number | null): string {
  if (typeof score !== "number" || Number.isNaN(score) || score < 0) {
    return "-";
  }
  return (score * 100).toFixed(2) + "%";
}

export function resolveJobTopLabel(job: SentimentJobItem): string {
  const labelKey = resolveJobTopLabelKey(job);
  if (!labelKey) {
    return "-";
  }
  return labelKey.charAt(0).toUpperCase() + labelKey.slice(1);
}

export function resolveJobTopLabelKey(job: SentimentJobItem): string | null {
  const counts = job.label_counts ?? {};
  let bestLabel: string | null = null;
  let bestCount = -1;
  for (const [label, count] of Object.entries(counts)) {
    if (typeof count !== "number") {
      continue;
    }
    if (count > bestCount) {
      bestCount = count;
      bestLabel = label;
    }
  }
  return bestLabel;
}

export function resolveJobAverageScore(job: SentimentJobItem): number {
  const counts = job.label_counts ?? {};
  if (Object.keys(counts).length === 0) {
    return -1;
  }

  let total = 0;
  for (const count of Object.values(counts)) {
    if (typeof count === "number") {
      total += count;
    }
  }

  if (total === 0) {
    return -1;
  }

  return total / Object.keys(counts).length / 100;
}
