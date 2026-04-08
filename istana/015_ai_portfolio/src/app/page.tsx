import { Navbar } from "@/components/layout/Navbar";
import { Hero } from "@/components/layout/Hero";
import { PortfolioGrid } from "@/components/layout/PortfolioGrid";
import { Footer } from "@/components/layout/Footer";
import { getAllPortfolios } from "@/services/portfolio";

export default function Home() {
  // Ambil data portofolio dari Markdown (Server-side rendering)
  const portfolios = getAllPortfolios();

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-black">
        <Hero />
        {/* Kirim data ke Client Component */}
        <PortfolioGrid items={portfolios} />
      </main>
      <Footer />
    </>
  );
}
