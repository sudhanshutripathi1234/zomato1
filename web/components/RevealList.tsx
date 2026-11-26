"use client";

import { useLayoutEffect, useRef, type ReactNode } from "react";
import gsap from "gsap";
import { prefersReducedMotion, registerMotion } from "@/lib/motion";

type RevealListProps = {
  watch: string;
  className?: string;
  children: ReactNode;
};

export function RevealList({ watch, className, children }: RevealListProps) {
  const ref = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    registerMotion();
    const root = ref.current;
    if (!root) return;
    const marked = root.querySelectorAll("[data-reveal]");
    const items = marked.length > 0 ? Array.from(marked) : Array.from(root.children);
    if (items.length === 0) return;

    if (prefersReducedMotion()) {
      gsap.set(items, { autoAlpha: 1, y: 0 });
      return;
    }

    const each = items.length > 8 ? 0.42 / items.length : 0.06;
    const tween = gsap.from(items, {
      autoAlpha: 0,
      y: 22,
      duration: 0.5,
      stagger: each,
      ease: "power2.out",
      clearProps: "transform,opacity,visibility",
    });

    return () => {
      tween.kill();
    };
  }, [watch]);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}
