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
      <main className="w-full flex flex-col items-center pt-28 px-4 md:px-0">
        {children}
      </main>
      <Footer />
    </>
  );
}
