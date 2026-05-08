"use client";

import { useEffect, useMemo, useState } from "react";
import axios, { AxiosError } from "axios";
import { useSession } from "next-auth/react";
import DashboardPageTitle from "@/components/layout/dashboard/DashboardPageTitle";
import DashboardPageContent from "@/components/layout/dashboard/DashboardPageContent";
import KeywordTable from "@/components/layout/dashboard/KeywordTable";
import TrendChart from "@/components/layout/dashboard/TrendChart";
import { FaArrowUp, FaArrowDown } from "react-icons/fa";
import { appToast } from "@/lib/toast";

type AnalysisSummaryResponse = {
  total_analyses: number;
  delta_from_yesterday: number;
  sentiment_counts: Record<string, number>;
  total_sentiments: number;
};

type KeywordResponse = {
  items: { word: string; count: number }[];
  sentiment?: string | null;
  job_id?: string | null;
};

type TrendItem = {
  date: string;
  positive: number;
  negative: number;
};

type TrendResponse = {
  items: TrendItem[];
};

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const [summary, setSummary] = useState<AnalysisSummaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [keywordsLoading, setKeywordsLoading] = useState(false);
  const [positiveKeywords, setPositiveKeywords] = useState<
    { word: string; count: number }[]
  >([]);
  const [negativeKeywords, setNegativeKeywords] = useState<
    { word: string; count: number }[]
  >([]);
  const [trendLoading, setTrendLoading] = useState(false);
  const [trendData, setTrendData] = useState<TrendItem[]>([]);

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
    "http://localhost:8000/api";

  useEffect(() => {
    const accessToken = session?.accessToken;
    if (!accessToken || status === "loading") {
      return;
    }

    let isActive = true;
    const fetchSummary = async () => {
      setLoading(true);
      try {
        const response = await axios.get<AnalysisSummaryResponse>(
          `${apiBaseUrl}/analyses/summary`,
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          },
        );
        if (!isActive) {
          return;
        }
        setSummary(response.data);
      } catch (err) {
        if (!isActive) {
          return;
        }
        const apiError = err as AxiosError;
        const message =
          typeof apiError.response?.data === "string"
            ? apiError.response?.data
            : apiError.message || "Gagal memuat ringkasan dashboard.";
        appToast.error(message);
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    };

    fetchSummary();
    return () => {
      isActive = false;
    };
  }, [apiBaseUrl, session?.accessToken, status]);

  useEffect(() => {
    const accessToken = session?.accessToken;
    if (!accessToken || status === "loading") {
      return;
    }

    let isActive = true;
    const fetchTrend = async () => {
      setTrendLoading(true);
      try {
        const response = await axios.get<TrendResponse>(
          `${apiBaseUrl}/analyses/trend?days=14`,
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          },
        );

        if (!isActive) {
          return;
        }

        setTrendData(response.data.items || []);
      } catch (err) {
        if (!isActive) {
          return;
        }
        const apiError = err as AxiosError;
        const message =
          typeof apiError.response?.data === "string"
            ? apiError.response?.data
            : apiError.message || "Gagal memuat tren analisis.";
        appToast.error(message);
      } finally {
        if (isActive) {
          setTrendLoading(false);
        }
      }
    };

    fetchTrend();
    return () => {
      isActive = false;
    };
  }, [apiBaseUrl, session?.accessToken, status]);

  useEffect(() => {
    const accessToken = session?.accessToken;
    if (!accessToken || status === "loading") {
      return;
    }

    let isActive = true;
    const fetchKeywords = async () => {
      setKeywordsLoading(true);
      try {
        const [positiveResponse, negativeResponse] = await Promise.all([
          axios.get<KeywordResponse>(
            `${apiBaseUrl}/dashboard/keywords?sentiment=positive&top=40`,
            {
              headers: {
                Authorization: `Bearer ${accessToken}`,
              },
            },
          ),
          axios.get<KeywordResponse>(
            `${apiBaseUrl}/dashboard/keywords?sentiment=negative&top=40`,
            {
              headers: {
                Authorization: `Bearer ${accessToken}`,
              },
            },
          ),
        ]);

        if (!isActive) {
          return;
        }

        setPositiveKeywords(positiveResponse.data.items || []);
        setNegativeKeywords(negativeResponse.data.items || []);
      } catch (err) {
        if (!isActive) {
          return;
        }
        const apiError = err as AxiosError;
        const message =
          typeof apiError.response?.data === "string"
            ? apiError.response?.data
            : apiError.message || "Gagal memuat word cloud.";
        appToast.error(message);
      } finally {
        if (isActive) {
          setKeywordsLoading(false);
        }
      }
    };

    fetchKeywords();
    return () => {
      isActive = false;
    };
  }, [apiBaseUrl, session?.accessToken, status]);

  const totalAnalyses = summary?.total_analyses ?? 0;
  const deltaFromYesterday = summary?.delta_from_yesterday ?? 0;
  const sentimentCounts = summary?.sentiment_counts ?? {};
  const totalSentiments = summary?.total_sentiments ?? 0;

  const positiveCount = sentimentCounts.positive ?? 0;
  const negativeCount = sentimentCounts.negative ?? 0;
  const neutralCount = sentimentCounts.neutral ?? 0;

  const percent = useMemo(() => {
    if (!totalSentiments) {
      return {
        positive: 0,
        negative: 0,
        neutral: 0,
      };
    }

    return {
      positive: Math.round((positiveCount / totalSentiments) * 100),
      negative: Math.round((negativeCount / totalSentiments) * 100),
      neutral: Math.round((neutralCount / totalSentiments) * 100),
    };
  }, [negativeCount, neutralCount, positiveCount, totalSentiments]);

  const deltaIndicator = deltaFromYesterday >= 0 ? "up" : "down";
  const deltaValue = Math.abs(deltaFromYesterday);

  return (
    <main className="w-full mx-auto flex flex-col gap-4">
      <DashboardPageTitle
        title="Dashboard"
        subtitle="Selamat datang di dashboard Anda"
      />
      <DashboardPageContent>
        <h1 className="font-bold text-3xl">
          Halo, {session?.user?.name || "Pengguna"}!
        </h1>
      </DashboardPageContent>
      <div className="flex items-center gap-4">
        <DashboardPageContent title="Total Analisis" line={false}>
          <h1 className="text-3xl font-black">
            {loading ? "-" : totalAnalyses}
          </h1>
          <p className="text-gray-600 text-sm flex items-center gap-1 mt-1">
            {deltaIndicator === "up" ? (
              <FaArrowUp className="text-green-500" />
            ) : (
              <FaArrowDown className="text-red-500" />
            )}
            {loading ? "Memuat..." : `${deltaValue} dari kemarin`}
          </p>
        </DashboardPageContent>
        <DashboardPageContent
          title="Sentimen Positif"
          line={false}
          className="bg-green-100!"
        >
          <h1 className="text-3xl font-black">
            {loading ? "-" : `${percent.positive}%`}
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            {loading ? "Memuat..." : `${positiveCount} Ulasan Positif`}
          </p>
        </DashboardPageContent>
        <DashboardPageContent
          title="Sentimen Negatif"
          line={false}
          className="bg-red-100!"
        >
          <h1 className="text-3xl font-black">
            {loading ? "-" : `${percent.negative}%`}
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            {loading ? "Memuat..." : `${negativeCount} Ulasan Negatif`}
          </p>
        </DashboardPageContent>
        <DashboardPageContent
          title="Sentimen Netral"
          line={false}
          className="bg-gray-100!"
        >
          <h1 className="text-3xl font-black">
            {loading ? "-" : `${percent.neutral}%`}
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            {loading ? "Memuat..." : `${neutralCount} Ulasan Netral`}
          </p>
        </DashboardPageContent>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <DashboardPageContent title="Frekuensi Keyword" line={false}>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:gap-6">
            <KeywordTable
              items={positiveKeywords}
              loading={keywordsLoading}
              emptyLabel="Belum ada kata kunci positif"
              tone="positive"
            />
            <KeywordTable
              items={negativeKeywords}
              loading={keywordsLoading}
              emptyLabel="Belum ada kata kunci negatif"
              tone="negative"
            />
          </div>
        </DashboardPageContent>
        <DashboardPageContent title="Tren Analisis" line={false}>
          <TrendChart data={trendData} loading={trendLoading} />
        </DashboardPageContent>
      </div>
    </main>
  );
}
