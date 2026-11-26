"use client";

import { useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import { SplitText } from "gsap/SplitText";
import { prefersReducedMotion, registerMotion } from "@/lib/motion";

type AppHeaderProps = {
  mode: string;
  model: string;
};

export function AppHeader({ mode, model }: AppHeaderProps) {
  const rootRef = useRef<HTMLElement>(null);
  const chip =
    mode.toLowerCase().includes("mock") || model === "mock"
      ? "Mode: Mock LLM · offline"
      : `Mode: ${mode} · ${model}`;

  useLayoutEffect(() => {
    registerMotion();
    const root = rootRef.current;
    if (!root || prefersReducedMotion()) return;

    const bits = root.querySelectorAll("[data-rise]");
    const rule = root.querySelector("[data-rule]");
    const title = root.querySelector("[data-title]");
    let split: SplitText | null = null;
    let titleTween: gsap.core.Tween | null = null;
    let cancelled = false;

    const intro = gsap.timeline({ defaults: { ease: "power2.out" } });
    if (bits.length) {
      intro.from(bits, { autoAlpha: 0, y: 12, duration: 0.45, stagger: 0.07 }, 0);
    }
    if (rule) {
      intro.from(rule, { scaleX: 0, duration: 0.5, ease: "power2.inOut" }, 0.22);
    }

    const playTitle = () => {
      if (cancelled || !title) return;
      split?.revert();
      gsap.set(title, { autoAlpha: 1 });
      split = SplitText.create(title, {
        type: "chars",
        aria: "auto",
      });
      titleTween = gsap.from(split.chars, {
        y: 18,
        opacity: 0,
        duration: 0.55,
        stagger: 0.02,
        ease: "expo.out",
      });
    };

    if (!document.fonts || document.fonts.status === "loaded") {
      playTitle();
    } else {
      if (title) gsap.set(title, { autoAlpha: 0 });
      document.fonts.ready.then(playTitle);
    }

    return () => {
      cancelled = true;
      intro.kill();
      titleTween?.kill();
      split?.revert();
    };
  }, []);

  return (
    <header ref={rootRef} className="pt-2">
      <div
        data-rise
        className="rounded-custom border border-white/25 bg-[#0a1a30] px-5 py-5 shadow-[0_18px_48px_rgba(0,0,0,0.45)] sm:px-7 sm:py-6"
      >
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/70">
              Dining, ranked
            </p>
            <h1
              data-title
              className="mt-2 font-serif text-4xl leading-[1.12] tracking-tight text-white sm:text-5xl lg:text-[52px]"
            >
              SPICE AI
            </h1>
            <span
              data-rule
              aria-hidden
              className="mt-3 block h-px w-14 origin-left bg-sky-300"
            />
          </div>
          <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-[11px] tracking-wide text-white">
            <span className="h-1.5 w-1.5 rounded-full bg-sky-300" aria-hidden />
            <span>{chip}</span>
          </div>
        </div>
        <p className="mt-4 max-w-2xl text-base font-normal leading-relaxed text-white/80 sm:text-lg">
          Filter real Zomato listings, then let AI rank and explain the best fits.
        </p>
      </div>
    </header>
  );
}
