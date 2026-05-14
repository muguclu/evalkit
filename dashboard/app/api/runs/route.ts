import { NextResponse } from "next/server";

import { loadAllRuns } from "@/lib/load";
import { summarize } from "@/lib/types";

export const dynamic = "force-dynamic";

export async function GET() {
  const runs = await loadAllRuns();
  return NextResponse.json(runs.map(summarize));
}
