"use client";

import { useRef, useState, type PointerEvent } from "react";
import gsap from "gsap";
import { fetchGeocode } from "@/lib/api";
import {
  destinationQuery,
  formatDistanceKm,
  GeoError,
  getCachedPosition,
  getCurrentPosition,
  googleMapsDirectionsUrl,
  haversineKm,
} from "@/lib/geo";
import { prefersReducedMotion } from "@/lib/motion";
import type { RecommendationItem } from "@/lib/types";

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
  const [distanceLabel, setDistanceLabel] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState<"distance" | null>(null);

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

  const query = destinationQuery({
    name: item.name,
    address: item.address,
    location: item.location,
  });

  async function handleDistance() {
    setBusy("distance");
    setStatus("Finding your location…");
    try {
      const [originResult, placeResult] = await Promise.allSettled([
        getCurrentPosition(),
        fetchGeocode(query),
      ]);

      if (originResult.status === "rejected") {
        const err = originResult.reason;
        setStatus(
          err instanceof GeoError
            ? err.message
            : "Could not read your current location.",
        );
        return;
      }
      if (placeResult.status === "rejected") {
        const err = placeResult.reason;
        const message =
          err && typeof err === "object" && "message" in err
            ? String((err as { message?: string }).message || "")
            : "";
        setStatus(
          message ||
            "Could not estimate distance. Make sure the API is running.",
        );
        return;
      }

      const origin = originResult.value;
      const place = placeResult.value;
      const km = haversineKm(origin, { lat: place.lat, lon: place.lon });
      setDistanceLabel(`${formatDistanceKm(km)} (approx. straight-line)`);
      setStatus(null);
    } finally {
      setBusy(null);
    }
  }

  function handleDirections() {
    setStatus(null);
    // Open Maps immediately — Google uses the device location for live routing.
    // Using any cached origin only when already available keeps the click instant.
    const url = googleMapsDirectionsUrl({
      destination: query,
      origin: getCachedPosition(),
    });
    const opened = window.open(url, "_blank", "noopener,noreferrer");
    if (!opened) {
      window.location.assign(url);
    }
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

      <div className="mt-4 flex flex-col gap-2 border-t border-border/50 pt-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-h-[1.25rem] text-xs text-text-muted">
          {distanceLabel ? (
            <span className="font-medium text-text-primary">{distanceLabel}</span>
          ) : null}
          {status ? <span className="block text-warning">{status}</span> : null}
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={busy !== null}
            onClick={handleDistance}
            className="inline-flex h-9 items-center justify-center rounded-[10px] border border-border bg-card-alt px-3 text-xs font-semibold text-text-primary transition hover:border-accent/40 hover:bg-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-60"
          >
            {busy === "distance" ? "Checking…" : "Show distance"}
          </button>
          <button
            type="button"
            disabled={busy !== null}
            onClick={handleDirections}
            className="inline-flex h-9 items-center justify-center rounded-[10px] bg-accent px-3 text-xs font-semibold text-on-accent transition hover:bg-accent-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-60"
          >
            Get directions
          </button>
        </div>
      </div>
    </article>
  );
}
