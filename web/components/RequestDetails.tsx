"use client";

import { useLayoutEffect, useRef, useState } from "react";
import gsap from "gsap";
import type { FilterMeta } from "@/lib/types";
import { prefersReducedMotion, registerMotion } from "@/lib/motion";

type RequestDetailsProps = {
  meta: FilterMeta;
  results: number;
};

export function RequestDetails({ meta, results }: RequestDetailsProps) {
  const [open, setOpen] = useState(false);
  const panelRef = useRef<HTMLPreElement>(null);
  const payload = {
    filters_applied: meta.filters_applied,
    candidate_count: meta.candidate_count,
    hard_match_count: meta.hard_match_count,
    results,
    used_llm: meta.used_llm,
    used_fallback: meta.used_fallback,
    llm_provider: meta.llm_provider,
  };

  useLayoutEffect(() => {
    registerMotion();
    const panel = panelRef.current;
    if (!panel || !open || prefersReducedMotion()) return;
    const tween = gsap.fromTo(
      panel,
      { height: 0, autoAlpha: 0 },
      { height: "auto", autoAlpha: 1, duration: 0.35, ease: "power2.out" },
    );
    return () => {
      tween.kill();
    };
  }, [open]);

  function toggle() {
    const panel = panelRef.current;
    if (open && panel && !prefersReducedMotion()) {
      gsap.to(panel, {
        height: 0,
        autoAlpha: 0,
        duration: 0.28,
        ease: "power2.inOut",
        overwrite: "auto",
        onComplete: () => setOpen(false),
      });
      return;
    }
    setOpen((value) => !value);
  }

  return (
    <section data-reveal className="overflow-hidden rounded-custom border border-border bg-card">
      <button
        type="button"
        onClick={toggle}
        aria-expanded={open}
        className="flex w-full cursor-pointer items-center justify-between px-5 py-4 text-left transition duration-200 hover:bg-card-alt focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-accent"
      >
        <span className="text-xs font-semibold uppercase tracking-wide text-text-muted">
          Request details
        </span>
        <span className="font-mono text-[11px] text-text-muted/70">
          JSON Payload {open ? "▴" : "▾"}
        </span>
      </button>
      {open ? (
        <pre
          ref={panelRef}
          className="overflow-x-auto border-t border-border/60 bg-inset px-5 py-4 font-mono text-[11px] leading-relaxed text-text-primary"
        >
          {JSON.stringify(payload, null, 2)}
        </pre>
      ) : null}
    </section>
  );
}
