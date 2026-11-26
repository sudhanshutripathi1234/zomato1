"use client";

import { useRef, type PointerEvent } from "react";
import gsap from "gsap";
import type { RecommendationItem } from "@/lib/types";
import { prefersReducedMotion } from "@/lib/motion";

type RecommendationCardProps = {
  item: RecommendationItem;
};

function formatCost(value: number | null): string {
  if (value == null) return "N/A";
  return `₹${Math.round(value).toLocaleString("en-IN")} for two`;
}

function formatRating(value: number | null): string {
  if (value == null) return "N/A";
  return value.toFixed(1);
}

export function RecommendationCard({ item }: RecommendationCardProps) {
  const first = item.rank === 1;
  const cardRef = useRef<HTMLElement>(null);

  function lift(event: PointerEvent<HTMLElement>, raised: boolean) {
    const el = cardRef.current;
    if (!el || event.pointerType !== "mouse" || prefersReducedMotion()) return;
    gsap.to(el, {
      y: raised ? -3 : 0,
      boxShadow: raised
        ? "0 12px 28px rgba(7, 20, 37, 0.08)"
        : "0 1px 2px rgba(7, 20, 37, 0.05)",
      duration: 0.35,
      ease: "power2.out",
      overwrite: "auto",
    });
  }

  return (
    <article
      ref={cardRef}
      data-reveal
      onPointerEnter={(event) => lift(event, true)}
      onPointerLeave={(event) => lift(event, false)}
      className="rounded-custom border border-border bg-card p-5 shadow-sm [@media(hover:hover)_and_(pointer:fine)]:hover:border-primary/40 sm:p-6"
    >
      <div className="flex flex-col justify-between gap-2.5 pb-3 sm:flex-row sm:items-center">
        <div className="flex items-center gap-3">
          <span
            className={
              first
                ? "flex h-7 w-7 items-center justify-center rounded-lg bg-primary font-mono text-xs font-bold text-on-accent shadow-sm"
                : "flex h-7 w-7 items-center justify-center rounded-lg border border-border bg-card-alt font-mono text-xs font-bold text-text-primary"
            }
          >
            #{item.rank}
          </span>
          <h3 className="font-serif text-xl tracking-tight text-text-primary sm:text-2xl">
            {item.name || "Unknown restaurant"}
          </h3>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs text-text-muted">
          <span className="font-medium text-text-primary">
            {item.cuisine || "Cuisine N/A"}
          </span>
          <span className="text-border">·</span>
          <span className="inline-flex items-center gap-1 font-mono font-semibold text-accent">
            <svg className="h-3.5 w-3.5 fill-accent" viewBox="0 0 24 24" aria-hidden>
              <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
            </svg>
            {formatRating(item.rating)}
          </span>
          <span className="text-border">·</span>
          <span>{formatCost(item.estimated_cost)}</span>
          <span className="text-border">·</span>
          <span className="text-text-muted/90">
            {item.location || "Location N/A"}
          </span>
        </div>
      </div>
      <div className="border-t border-border/50 pt-3">
        <p className="line-clamp-2 text-sm leading-relaxed text-text-muted">
          <span className="mr-1.5 font-mono text-[11px] font-semibold uppercase tracking-wider text-accent">
            AI Fit:
          </span>
          {item.explanation || "No explanation available."}
        </p>
      </div>
    </article>
  );
}
