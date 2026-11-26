"use client";

import { useLayoutEffect, useRef, type ReactNode } from "react";
import gsap from "gsap";
import { prefersReducedMotion, registerMotion } from "@/lib/motion";

type RiseInProps = {
  children: ReactNode;
  className?: string;
  delay?: number;
};

export function RiseIn({ children, className, delay = 0 }: RiseInProps) {
  const ref = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    registerMotion();
    const el = ref.current;
    if (!el) return;
    if (prefersReducedMotion()) {
      gsap.set(el, { autoAlpha: 1, y: 0 });
      return;
    }

    const tween = gsap.from(el, {
      autoAlpha: 0,
      y: 18,
      duration: 0.55,
      delay,
      ease: "power2.out",
      clearProps: "opacity,visibility,transform",
    });

    return () => {
      tween.kill();
    };
  }, [delay]);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}
