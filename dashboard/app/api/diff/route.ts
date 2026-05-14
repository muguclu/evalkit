import { NextResponse } from "next/server";

import { diffRuns } from "@/lib/diff";
import { loadRun } from "@/lib/load";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const a = url.searchParams.get("a");
  const b = url.searchParams.get("b");
  if (!a || !b) {
    return NextResponse.json(
      { error: "both 'a' (baseline) and 'b' (candidate) query params are required" },
      { status: 400 },
    );
  }
  try {
    const [baseline, candidate] = await Promise.all([loadRun(a), loadRun(b)]);
    return NextResponse.json(diffRuns(baseline, candidate));
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === "ENOENT") {
      return NextResponse.json({ error: "one of the runs was not found" }, { status: 404 });
    }
    throw e;
  }
}
