"use client";

import { useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import { prefersReducedMotion, registerMotion } from "@/lib/motion";

type MetricStripProps = {
  candidateCount: number;
  hardMatchCount: number;
  results: number;
};

function CountValue({ value, className }: { value: number; className: string }) {
  const ref = useRef<HTMLSpanElement>(null);

  useLayoutEffect(() => {
    registerMotion();
    const el = ref.current;
    if (!el) return;
    if (prefersReducedMotion()) {
      el.textContent = String(value);
      return;
    }

    const proxy = { n: 0 };
    el.textContent = "0";
    const tween = gsap.to(proxy, {
      n: value,
      duration: 0.7,
      ease: "power2.out",
      snap: { n: 1 },
      onUpdate: () => {
        el.textContent = String(Math.round(proxy.n));
      },
    });

    return () => {
      tween.kill();
    };
  }, [value]);

  return <span ref={ref} className={className} aria-label={String(value)} />;
}

export function MetricStrip({
  candidateCount,
  hardMatchCount,
  results,
}: MetricStripProps) {
  return (
    <section data-reveal className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div className="flex items-center justify-between rounded-custom border border-border bg-card px-4 py-3.5">
        <span className="text-xs font-medium text-text-muted">
          Candidates sent to AI
        </span>
        <CountValue
          value={candidateCount}
          className="rounded border border-border bg-inset px-2 py-0.5 font-mono text-base font-bold text-text-primary"
        />
      </div>
      <div className="flex items-center justify-between rounded-custom border border-border bg-card px-4 py-3.5">
        <span className="text-xs font-medium text-text-muted">
          Hard filter matches
        </span>
        <CountValue
          value={hardMatchCount}
          className="rounded border border-border bg-inset px-2 py-0.5 font-mono text-base font-bold text-text-primary"
        />
      </div>
      <div className="flex items-center justify-between rounded-custom border border-border bg-card px-4 py-3.5">
        <span className="text-xs font-medium text-text-muted">Results</span>
        <CountValue
          value={results}
          className="rounded border border-accent/30 bg-accent/10 px-2.5 py-0.5 font-mono text-base font-bold text-accent"
        />
      </div>
    </section>
  );
}
