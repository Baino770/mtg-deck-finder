"use client";

import { useState } from "react";
import { getRandomGuild } from "@/lib/guilds";
import { useGuildTheme } from "@/lib/guilds/GuildThemeProvider";

export function DeckSearchForm() {
  const [value, setValue] = useState("");
  const [hint, setHint] = useState("Enter your card list above");
  const { setGuild } = useGuildTheme();

  const lineCount = value.split("\n").filter((l) => l.trim()).length;

  function handleChange(next: string) {
    setValue(next);
    const lines = next.split("\n").filter((l) => l.trim()).length;
    setHint(
      lines > 0
        ? `${lines} line${lines !== 1 ? "s" : ""} entered`
        : "Enter your card list above"
    );
  }

  function handleFindCheapest() {
    const trimmed = value.trim();
    if (!trimmed) {
      setHint("Please enter a deck list first");
      return;
    }

    // TODO: replace with real colour-identity detection once the
    // Scryfall lookup is wired up to the FastAPI backend. For now this
    // demonstrates the mechanic: theme only changes on submit, never
    // while typing.
    const matched = getRandomGuild();
    setGuild(matched, true);
    setHint(
      `Matched to ${matched.name} (placeholder — detection not wired up yet)`
    );
  }

  return (
    <div className="relative z-10 mx-auto w-full max-w-[520px] px-8 pb-2">
      <div
        className="mb-2.5 flex items-center gap-2 text-[11px] font-medium tracking-[2px] uppercase"
        style={{ color: "var(--guild-c1)", transition: "color 0.6s ease" }}
      >
        <div className="h-px flex-1 bg-canvas-border" />
        <span>Your deck list</span>
        <div className="h-px flex-1 bg-canvas-border" />
      </div>

      <textarea
        rows={6}
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        placeholder={
          "4 Lightning Bolt\n4 Goblin Guide\n4 Monastery Swiftspear\n2 Shard Volley\n4 Eidolon of the Great Revel\n…"
        }
        className="w-full resize-none rounded-b-sm border border-canvas-border bg-canvas-surface px-4 py-3.5 font-mono text-sm leading-7 text-canvas-text outline-none placeholder:text-canvas-muted"
        style={{
          borderTopWidth: "3px",
          borderTopColor: "var(--guild-c1)",
          transition: "border-top-color 0.6s ease",
        }}
      />

      <div className="mt-3 flex items-center justify-between">
        <span className="text-xs text-canvas-muted">
          {lineCount > 0 ? hint : hint}
        </span>
        <button
          onClick={handleFindCheapest}
          className="flex items-center gap-2 rounded-sm px-6 py-2.5 font-display text-lg tracking-wider text-[#100f0e] transition-[filter] hover:brightness-110 active:scale-[0.98]"
          style={{
            background: "var(--guild-c1)",
            transition: "background 0.6s ease",
          }}
        >
          FIND CHEAPEST
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
      </div>
    </div>
  );
}
