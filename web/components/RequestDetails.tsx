"use client";

import { useState } from "react";
import type { FilterMeta } from "@/lib/types";

type RequestDetailsProps = {
  meta: FilterMeta;
  results: number;
};

export function RequestDetails({ meta, results }: RequestDetailsProps) {
  const [open, setOpen] = useState(false);
  const payload = {
    filters_applied: meta.filters_applied,
    candidate_count: meta.candidate_count,
    hard_match_count: meta.hard_match_count,
    results,
    used_llm: meta.used_llm,
    used_fallback: meta.used_fallback,
    llm_provider: meta.llm_provider,
  };

  return (
    <section className="overflow-hidden rounded-custom border border-border bg-card">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-5 py-4 text-left transition hover:bg-[#161616]"
      >
        <span className="text-xs font-semibold uppercase tracking-wide text-text-muted">
          Request details
        </span>
        <span className="font-mono text-[11px] text-text-muted/70">
          JSON Payload {open ? "▴" : "▾"}
        </span>
      </button>
      {open ? (
        <pre className="overflow-x-auto border-t border-border/60 bg-[#0A0A0A] px-5 py-4 font-mono text-[11px] leading-relaxed text-[#D4D4D4]">
          {JSON.stringify(payload, null, 2)}
        </pre>
      ) : null}
    </section>
  );
}
