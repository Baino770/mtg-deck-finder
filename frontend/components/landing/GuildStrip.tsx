"use client";

import { GUILDS } from "@/lib/guilds";
import { useGuildTheme } from "@/lib/guilds/GuildThemeProvider";

export function GuildStrip() {
  const { guild, setGuild } = useGuildTheme();

  return (
    <div className="relative z-10 mx-8 mt-8 flex overflow-hidden rounded-sm border border-canvas-border">
      {GUILDS.map((g) => {
        const isActive = g.name === guild.name;
        return (
          <button
            key={g.name}
            onClick={() => setGuild(g, true)}
            className={`flex-1 border-r border-canvas-border px-1 py-2.5 text-[10px] font-medium tracking-wider uppercase transition-colors last:border-r-0 hover:bg-white/5 ${
              isActive ? "" : "text-canvas-muted hover:text-canvas-text"
            }`}
            style={
              isActive
                ? {
                    color: "var(--guild-c1)",
                    background: "rgba(255,255,255,0.05)",
                    borderBottom: "2px solid var(--guild-c1)",
                    transition: "color 0.6s ease, border-color 0.6s ease",
                  }
                : undefined
            }
          >
            {g.name}
          </button>
        );
      })}
    </div>
  );
}
