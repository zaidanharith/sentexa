import Footer from "@/components/layout/Footer";
import Navbar from "@/components/layout/Navbar";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <Navbar />
      <main className="container mx-auto max-w-7xl flex flex-col items-center pt-24 px-4 flex-1">
        {children}
      </main>
      <Footer />
    </>
  );
}
