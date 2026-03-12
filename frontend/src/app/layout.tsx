import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const plusJakartaSans = Plus_Jakarta_Sans({
  variable: "--font-plus-jakarta-sans",
  subsets: ["latin"],
  weight: ["200", "300", "400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Sentexa - Aplikasi Analisis Sentimen Berbasis NLP",
  description:
    "Sentexa adalah aplikasi web analisis sentimen berbasis Natural Language Processing (NLP) yang mengklasifikasikan teks menjadi positif, negatif, atau netral, dilengkapi preprocessing, pemodelan AI, dan visualisasi hasil melalui antarmuka web yang interaktif dan mudah digunakan.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id">
      <body className={`${plusJakartaSans.variable} antialiased`}>
        <div className="min-h-screen flex flex-col">{children}</div>
      </body>
    </html>
  );
}
