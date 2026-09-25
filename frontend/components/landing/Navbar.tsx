"use client";

import { useGuildTheme } from "@/lib/guilds/GuildThemeProvider";

export function Navbar() {
  const { guild } = useGuildTheme();

  return (
    <nav className="relative z-10 flex items-center justify-between border-b border-canvas-border px-8 py-5">
      <div className="font-display text-3xl leading-none tracking-wider">
        DECK
        <span
          style={{ color: "var(--guild-c1)", transition: "color 0.6s ease" }}
        >
          FINDER
        </span>
      </div>

      <div className="flex items-center gap-5">
        <span className="text-sm text-canvas-muted">Vendors</span>
        <span className="text-sm text-canvas-muted">How it works</span>
        <span
          className="rounded-sm border px-2.5 py-1 text-[11px] font-medium tracking-wider uppercase"
          style={{
            color: "var(--guild-c1)",
            borderColor: "var(--guild-c1)",
            transition: "color 0.6s ease, border-color 0.6s ease",
          }}
        >
          {guild.name} · {guild.pair.join("")}
        </span>
      </div>
    </nav>
  );
}
