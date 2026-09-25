interface DecorativeFigureProps {
  flip?: boolean;
  className?: string;
}

/**
 * Abstract two-tone line figure, drawn with the two active guild
 * colours. Purely decorative - mirrored for the left/right edges of
 * the hero section.
 */
export function DecorativeFigure({ flip, className }: DecorativeFigureProps) {
  return (
    <svg
      viewBox="0 0 130 300"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      className={className}
      style={flip ? { transform: "scaleX(-1)" } : undefined}
    >
      <path
        d="M65 8 C28 36, 10 72, 18 108 C26 144, 54 154, 50 190 C46 226, 18 244, 26 280"
        stroke="var(--guild-c1)"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
        style={{ transition: "stroke 0.6s ease" }}
      />
      <path
        d="M65 8 C102 36, 120 72, 112 108 C104 144, 76 154, 80 190 C84 226, 112 244, 104 280"
        stroke="var(--guild-c2)"
        strokeWidth="1.5"
        fill="none"
        strokeLinecap="round"
        opacity="0.7"
        style={{ transition: "stroke 0.6s ease" }}
      />
      <circle cx="65" cy="8" r="5" fill="var(--guild-c1)" style={{ transition: "fill 0.6s ease" }} />
    </svg>
  );
}
