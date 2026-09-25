export function Hero() {
  return (
    <div className="relative z-10 flex flex-col items-center px-8 pt-16 pb-9 text-center">
      <div
        className="mb-4 text-[11px] font-medium tracking-[3px] uppercase"
        style={{ color: "var(--guild-c1)", transition: "color 0.6s ease" }}
      >
        UK Magic: The Gathering price optimiser
      </div>

      <h1 className="font-display text-[78px] leading-[0.92] tracking-wider">
        FIND YOUR
        <br />
        DECK FOR{" "}
        <span
          style={{ color: "var(--guild-c1)", transition: "color 0.6s ease" }}
        >
          LESS
        </span>
      </h1>

      <p className="mx-auto mt-4 max-w-sm text-sm leading-7 text-canvas-muted">
        Paste your list. We search Magic Madhouse, Troll Trader, and more —
        then solve for the cheapest combination across all UK vendors.
      </p>

      <div
        className="mx-auto mt-6 h-[3px] w-12"
        style={{
          background: "linear-gradient(90deg, var(--guild-c1), var(--guild-c2))",
          transition: "background 0.6s ease",
        }}
      />
    </div>
  );
}
