import Link from "next/link";

export default function NotFound() {
  return (
    <div className="card text-center">
      <h1 className="text-lg font-semibold">Not found</h1>
      <p className="mt-2 text-sm text-ink-muted">
        That run does not exist on disk.
      </p>
      <Link
        href="/"
        className="mt-4 inline-block text-sm text-accent-violet hover:underline"
      >
        ← Back to runs
      </Link>
    </div>
  );
}
