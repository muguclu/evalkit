import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "EvalKit Dashboard",
  description: "Structured LLM evaluation results.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-bg-border bg-bg-panel/60 backdrop-blur">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
              <Link href="/" className="flex items-baseline gap-2">
                <span className="font-mono text-lg font-semibold text-ink-base">
                  evalkit
                </span>
                <span className="text-xs text-ink-dim">
                  structured LLM evals
                </span>
              </Link>
              <nav className="flex items-center gap-5 text-sm">
                <Link
                  href="/"
                  className="text-ink-muted transition hover:text-ink-base"
                >
                  Runs
                </Link>
                <Link
                  href="/compare"
                  className="text-ink-muted transition hover:text-ink-base"
                >
                  Compare
                </Link>
                <a
                  href="https://github.com/muguclu/evalkit"
                  target="_blank"
                  rel="noreferrer"
                  className="text-ink-muted transition hover:text-ink-base"
                >
                  GitHub
                </a>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
