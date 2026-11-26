"use client";

import { useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import type { UiError } from "@/lib/types";
import { prefersReducedMotion, registerMotion } from "@/lib/motion";

export function LoadingCard({ restaurantCount }: { restaurantCount: number }) {
  const iconRef = useRef<HTMLDivElement>(null);
  const barRef = useRef<HTMLSpanElement>(null);

  useLayoutEffect(() => {
    registerMotion();
    const icon = iconRef.current;
    const bar = barRef.current;
    if (!icon || !bar || prefersReducedMotion()) return;

    const spin = gsap.to(icon, {
      rotation: 360,
      duration: 1.6,
      repeat: -1,
      ease: "none",
      transformOrigin: "50% 50%",
    });
    const sweep = gsap.fromTo(
      bar,
      { scaleX: 0.18, xPercent: -30 },
      {
        scaleX: 0.55,
        xPercent: 90,
        duration: 1.05,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
        transformOrigin: "left center",
      },
    );

    return () => {
      spin.kill();
      sweep.kill();
    };
  }, []);

  return (
    <section
      className="space-y-4 rounded-custom border border-border bg-card p-8 text-center"
      aria-live="polite"
      aria-busy="true"
    >
      <div
        ref={iconRef}
        className="mx-auto inline-flex h-12 w-12 items-center justify-center rounded-full border border-accent/30 bg-accent/10 text-accent"
      >
        <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" aria-hidden>
          <circle cx="11" cy="11" r="6.5" stroke="currentColor" strokeWidth="1.8" />
          <path d="M16 16.5 20 20.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
      </div>
      <div className="mx-auto h-1 w-40 overflow-hidden rounded-full bg-inset" aria-hidden>
        <span ref={barRef} className="block h-full w-full rounded-full bg-accent" />
      </div>
      <div className="mx-auto max-w-md space-y-1">
        <p className="font-serif text-lg text-text-primary sm:text-xl">
          Finding matches and asking the AI to rank them…
        </p>
        <p className="text-xs text-text-muted">
          Filtering {restaurantCount.toLocaleString()} restaurant listings against
          your budget & rating constraints.
        </p>
      </div>
    </section>
  );
}

export function EmptyCard({ message }: { message?: string | null }) {
  return (
    <section className="space-y-4 rounded-custom border border-border bg-card p-8 text-center sm:p-10" role="status">
      <div className="mx-auto inline-flex h-12 w-12 items-center justify-center rounded-full border border-warning-border bg-warning-bg text-warning">
        <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" aria-hidden>
          <path d="M12 8v5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          <circle cx="12" cy="16.5" r="1" fill="currentColor" />
          <circle cx="12" cy="12" r="8.25" stroke="currentColor" strokeWidth="1.8" />
        </svg>
      </div>
      <div className="mx-auto max-w-lg space-y-2">
        <h3 className="font-serif text-xl text-text-primary">
          {message || "No restaurants matched these filters."}
        </h3>
        <p className="text-sm leading-relaxed text-text-muted">
          Try a broader location, different cuisine, lower min rating, or another
          budget.
        </p>
      </div>
    </section>
  );
}

export function ErrorCard({ error }: { error: UiError }) {
  return (
    <section className="space-y-4 rounded-custom border border-error-border bg-card p-8 sm:p-10" role="alert">
      <div className="flex items-start gap-4">
        <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-custom border border-error-border bg-error-bg text-error">
          <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" aria-hidden>
            <path d="M12 8v5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            <circle cx="12" cy="16.5" r="1" fill="currentColor" />
            <circle cx="12" cy="12" r="8.25" stroke="currentColor" strokeWidth="1.8" />
          </svg>
        </div>
        <div className="flex-1 space-y-2">
          <h3 className="font-serif text-xl text-text-primary">{error.title}</h3>
          <p className="text-sm leading-relaxed text-text-muted">{error.message}</p>
        </div>
      </div>
    </section>
  );
}
