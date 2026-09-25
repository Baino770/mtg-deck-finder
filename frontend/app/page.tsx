import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { DeckSearchForm } from "@/components/landing/DeckSearchForm";
import { GuildStrip } from "@/components/landing/GuildStrip";
import { FeatureStrip } from "@/components/landing/FeatureStrip";
import { NoiseTexture } from "@/components/landing/NoiseTexture";
import { DecorativeFigure } from "@/components/landing/DecorativeFigure";
import { ThemeTransitionOverlay } from "@/components/landing/ThemeTransitionOverlay";

export default function Home() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-canvas-bg">
      <ThemeTransitionOverlay />
      <NoiseTexture />

      <DecorativeFigure className="pointer-events-none absolute top-[70px] left-0 z-[1] w-[130px] opacity-90" />
      <DecorativeFigure
        flip
        className="pointer-events-none absolute top-[70px] right-0 z-[1] w-[130px] opacity-90"
      />

      <Navbar />
      <Hero />
      <DeckSearchForm />
      <GuildStrip />
      <FeatureStrip />

      <div className="h-16" />
    </main>
  );
}
