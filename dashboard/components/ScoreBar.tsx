import clsx from "clsx";

export function ScoreBar({
  score,
  passed,
  width = "w-32",
}: {
  score: number;
  passed?: boolean;
  width?: string;
}) {
  const pct = Math.max(0, Math.min(1, score)) * 100;
  const color =
    passed === false
      ? "bg-accent-red"
      : passed === true
      ? "bg-accent-green"
      : pct >= 70
      ? "bg-accent-green"
      : pct >= 40
      ? "bg-accent-amber"
      : "bg-accent-red";

  return (
    <div className="flex items-center gap-2">
      <div
        className={clsx(
          "h-1.5 overflow-hidden rounded-full bg-bg-border",
          width,
        )}
      >
        <div
          className={clsx("h-full transition-all", color)}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="font-mono text-xs text-ink-muted">
        {score.toFixed(2)}
      </span>
    </div>
  );
}
