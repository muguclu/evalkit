export function fmtPercent(value: number, digits = 1): string {
  return `${(value * 100).toFixed(digits)}%`;
}

export function fmtScore(value: number, digits = 2): string {
  return value.toFixed(digits);
}

export function fmtCost(usd: number): string {
  if (usd === 0) return "$0";
  if (usd < 0.0001) return `$${(usd * 1000).toFixed(3)}m`;
  if (usd < 0.01) return `$${usd.toFixed(4)}`;
  return `$${usd.toFixed(3)}`;
}

export function fmtLatency(ms: number): string {
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function fmtRelativeDate(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function fmtDelta(delta: number, suffix = ""): { text: string; tone: "good" | "bad" | "neutral" } {
  const sign = delta > 0 ? "+" : "";
  const tone = delta > 0.005 ? "good" : delta < -0.005 ? "bad" : "neutral";
  return { text: `${sign}${delta.toFixed(3)}${suffix}`, tone };
}
