import fs from "node:fs/promises";
import path from "node:path";

import type { RunResult } from "./types";

// EvalKit runs/ directory is at the project root.
// dashboard/ is at the same level, so go up one.
export const RUNS_DIR = path.resolve(process.cwd(), "..", "runs");

export async function listRunIds(): Promise<string[]> {
  try {
    const entries = await fs.readdir(RUNS_DIR, { withFileTypes: true });
    const dirs: { id: string; mtime: number }[] = [];
    for (const e of entries) {
      if (!e.isDirectory()) continue;
      const resultsPath = path.join(RUNS_DIR, e.name, "results.json");
      try {
        const stat = await fs.stat(resultsPath);
        dirs.push({ id: e.name, mtime: stat.mtimeMs });
      } catch {
        // Skip directories without results.json
      }
    }
    return dirs.sort((a, b) => b.mtime - a.mtime).map((d) => d.id);
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === "ENOENT") return [];
    throw e;
  }
}

export async function loadRun(runId: string): Promise<RunResult> {
  const file = path.join(RUNS_DIR, runId, "results.json");
  const raw = await fs.readFile(file, "utf-8");
  return JSON.parse(raw) as RunResult;
}

export async function loadAllRuns(): Promise<RunResult[]> {
  const ids = await listRunIds();
  return Promise.all(ids.map(loadRun));
}
