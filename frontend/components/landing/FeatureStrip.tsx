const FEATURES = [
  { label: "Vendors", value: "4 stores" },
  { label: "Method", value: "ILP solver" },
  { label: "Prices", value: "Live" },
  { label: "Savings", value: "vs single vendor" },
] as const;

export function FeatureStrip() {
  return (
    <div className="relative z-10 mx-8 mt-4 flex overflow-hidden rounded-sm border border-canvas-border">
      {FEATURES.map((f) => (
        <div
          key={f.label}
          className="flex-1 border-r border-canvas-border px-3.5 py-4 last:border-r-0"
        >
          <div className="mb-1 text-[10px] font-medium tracking-wider text-canvas-muted uppercase">
            {f.label}
          </div>
          <div
            className="font-display text-xl tracking-wide"
            style={{ color: "var(--guild-c2)", transition: "color 0.6s ease" }}
          >
            {f.value}
          </div>
        </div>
      ))}
    </div>
  );
}
