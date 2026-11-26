"use client";

import { useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { prefersReducedMotion, registerMotion } from "@/lib/motion";

export function FoodBackdrop() {
  const photoRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    registerMotion();
    const photo = photoRef.current;
    if (!photo || prefersReducedMotion()) return;

    const tween = gsap.fromTo(
      photo,
      { yPercent: 0 },
      {
        yPercent: -40,
        ease: "none",
        scrollTrigger: {
          trigger: document.documentElement,
          start: "top top",
          end: "bottom bottom",
          scrub: 0.8,
          invalidateOnRefresh: true,
        },
      },
    );

    const refresh = () => ScrollTrigger.refresh();
    const observer = new ResizeObserver(refresh);
    observer.observe(document.body);

    return () => {
      observer.disconnect();
      tween.scrollTrigger?.kill();
      tween.kill();
    };
  }, []);

  return (
    <div className="food-backdrop" aria-hidden>
      <div ref={photoRef} className="food-backdrop__photo" />
      <div className="food-backdrop__wash" />
    </div>
  );
}
