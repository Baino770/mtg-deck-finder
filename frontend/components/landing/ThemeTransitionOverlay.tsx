"use client";

import { useGuildTheme } from "@/lib/guilds/GuildThemeProvider";

export function ThemeTransitionOverlay() {
  const { isTransitioning } = useGuildTheme();
  return (
    <div className={`theme-flash ${isTransitioning ? "is-active" : ""}`} />
  );
}
