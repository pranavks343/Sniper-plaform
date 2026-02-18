'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

/** Fade + slide up on mount */
export function useFadeUp(
  selector: string,
  options: { stagger?: number; delay?: number; duration?: number } = {}
) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        selector,
        { opacity: 0, y: 28 },
        {
          opacity: 1,
          y: 0,
          duration: options.duration ?? 0.65,
          stagger: options.stagger ?? 0.08,
          delay: options.delay ?? 0,
          ease: 'power3.out',
        }
      );
    }, ref);
    return () => ctx.revert();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return ref;
}

/** Stagger children on scroll enter */
export function useScrollReveal(
  selector: string,
  options: { stagger?: number; once?: boolean } = {}
) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        selector,
        { opacity: 0, y: 36 },
        {
          opacity: 1,
          y: 0,
          duration: 0.7,
          stagger: options.stagger ?? 0.1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: selector,
            start: 'top 88%',
            once: options.once ?? true,
          },
        }
      );
    }, ref);
    return () => ctx.revert();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return ref;
}

/** Counter number animation */
export function useCountUp(target: number, duration = 1.4) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obj = { val: 0 };
    gsap.to(obj, {
      val: target,
      duration,
      ease: 'power2.out',
      onUpdate: () => {
        el.textContent = obj.val.toFixed(0);
      },
    });
  }, [target, duration]);

  return ref;
}
