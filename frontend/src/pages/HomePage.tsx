import { HeroSection } from "@/components/HeroSection";
import { SourceIcons } from "@/components/SourceIcons";
import { TrustIndicators } from "@/components/TrustIndicators";
import { Footer } from "@/components/Footer";

export default function HomePage() {
  return (
    <main className="min-h-screen">
      <HeroSection />
      <SourceIcons />
      <TrustIndicators />
      <Footer />
    </main>
  );
}