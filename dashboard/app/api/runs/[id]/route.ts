import { NextResponse } from "next/server";

import { loadRun } from "@/lib/load";

export const dynamic = "force-dynamic";

export async function GET(
  _request: Request,
  { params }: { params: { id: string } },
) {
  try {
    const run = await loadRun(params.id);
    return NextResponse.json(run);
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === "ENOENT") {
      return NextResponse.json({ error: "run not found" }, { status: 404 });
    }
    throw e;
  }
}
