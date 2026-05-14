import clsx from "clsx";

export function StatusBadge({
  passed,
  size = "md",
}: {
  passed: boolean;
  size?: "sm" | "md";
}) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-full border font-medium",
        size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-0.5 text-xs",
        passed
          ? "border-accent-green/30 bg-accent-green/10 text-accent-green"
          : "border-accent-red/30 bg-accent-red/10 text-accent-red",
      )}
    >
      <span
        className={clsx(
          "h-1.5 w-1.5 rounded-full",
          passed ? "bg-accent-green" : "bg-accent-red",
        )}
      />
      {passed ? "pass" : "fail"}
    </span>
  );
}
