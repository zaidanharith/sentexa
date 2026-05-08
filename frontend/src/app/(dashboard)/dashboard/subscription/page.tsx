import React from "react";
import { Check, X, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import DashboardPageContent from "@/components/layout/dashboard/DashboardPageContent"; // Sesuaikan path ini

export default function SubscriptionDashboardPage() {
  return (
    <main className="w-full max-w-5xl mx-auto pb-10">
      <DashboardPageContent
        title="Paket Langganan"
        subtitle="Kelola dan pilih paket yang sesuai dengan kebutuhan analisis Anda"
        line={true}
      >
        {/* 1. Grid Paket (Free & Premium) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          
          {/* Paket Gratis */}
          <Card className="border-slate-200 shadow-none">
            <CardHeader>
              <Badge variant="secondary" className="w-fit mb-1">Free</Badge>
              <CardTitle className="text-2xl font-bold">Gratis</CardTitle>
              <CardDescription>Fitur esensial untuk mencoba layanan</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" /> 100 Analisis per bulan
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" /> Akses Riwayat 7 Hari
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <X className="h-4 w-4" /> Ekspor Laporan CSV/PDF
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full" disabled>
                Paket Saat Ini
              </Button>
            </CardFooter>
          </Card>

          {/* Paket Premium */}
          <Card className="border-slate-900 bg-slate-900 text-white shadow-md">
            <CardHeader>
              <div className="flex justify-between items-start">
                <Badge className="bg-yellow-500 text-slate-900 border-none hover:bg-yellow-600">Premium</Badge>
              </div>
              <CardTitle className="text-2xl font-bold mt-2">Premium</CardTitle>
              <CardDescription className="text-slate-400">Akses penuh tanpa batas</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-yellow-500" /> Analisis Tak Terbatas
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-yellow-500" /> Prediksi Tren Berbasis AI
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-yellow-500" /> Ekspor Data Mentah & PDF
              </div>
            </CardContent>
            <CardFooter>
              <Button className="w-full bg-yellow-500 text-slate-900 hover:bg-yellow-600 font-bold border-none">
                Tingkatkan Sekarang
              </Button>
            </CardFooter>
          </Card>
        </div>

        {/* 2. Tabel Perbandingan Fitur */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-slate-800">Perbandingan Fitur</h2>
          <div className="rounded-xl border border-slate-200 overflow-hidden bg-white">
            <Table>
              <TableHeader className="bg-slate-50">
                <TableRow>
                  <TableHead className="w-[40%]">Fitur Utama</TableHead>
                  <TableHead className="text-center">Free</TableHead>
                  <TableHead className="text-center">Premium</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Total Review per Bulan</TableCell>
                  <TableCell className="text-center">100</TableCell>
                  <TableCell className="text-center font-bold text-green-600">Unlimited</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Analisis Sentimen AI</TableCell>
                  <TableCell className="text-center"><Check className="mx-auto h-4 w-4 text-green-500" /></TableCell>
                  <TableCell className="text-center"><Check className="mx-auto h-4 w-4 text-green-500" /></TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Ekspor Laporan</TableCell>
                  <TableCell className="text-center"><X className="mx-auto h-4 w-4 text-slate-300" /></TableCell>
                  <TableCell className="text-center"><Check className="mx-auto h-4 w-4 text-green-500" /></TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Dukungan Prioritas</TableCell>
                  <TableCell className="text-center"><X className="mx-auto h-4 w-4 text-slate-300" /></TableCell>
                  <TableCell className="text-center"><Check className="mx-auto h-4 w-4 text-green-500" /></TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </div>
      </DashboardPageContent>
    </main>
  );
}