import gsap from "gsap";
import { ScrollToPlugin } from "gsap/ScrollToPlugin";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";

let registered = false;

export function registerMotion() {
  if (registered || typeof window === "undefined") return;
  gsap.registerPlugin(ScrollToPlugin, ScrollTrigger, SplitText);
  registered = true;
}

export function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}
