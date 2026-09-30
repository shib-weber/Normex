import { useEffect, useRef, useState, useCallback } from "react";

/* ------------------------------------------------------------------ *
 * Capability + preference detection
 * Centralised so every effect agrees on what the device can handle.
 * ------------------------------------------------------------------ */

const mq = (q) => (typeof window !== "undefined" ? window.matchMedia(q) : { matches: false });

export function prefersReducedMotion() {
  return mq("(prefers-reduced-motion: reduce)").matches;
}

export function isTouchDevice() {
  return typeof window !== "undefined" && window.matchMedia("(hover: none)").matches;
}

export function isLowPower() {
  if (typeof navigator === "undefined") return false;
  const cores = navigator.hardwareConcurrency || 0;
  const mem = navigator.deviceMemory || 0;
  if (cores && cores <= 2) return true;
  if (mem && mem <= 2) return true;
  if (isTouchDevice() && cores && cores <= 4) return true;
  return false;
}

/** Full-fat motion: rich animation only where it is safe and wanted. */
export function motionAllowed() {
  if (typeof window === "undefined") return false;
  if (prefersReducedMotion()) return false;
  if (isTouchDevice()) return false;
  return !isLowPower();
}

/** Cheap decorative motion: still fine on mobile, just less of it. */
export function ambientAllowed() {
  if (typeof window === "undefined") return false;
  if (prefersReducedMotion()) return false;
  if (isLowPower()) return false;
  const conn = navigator.connection;
  if (conn && (conn.saveData || /2g/.test(conn.effectiveType || ""))) return false;
  return true;
}

/* ------------------------------------------------------------------ *
 * Smooth, momentum-based scrolling
 * rAF-driven exponential easing on the window scroller. Disabled for
 * reduced-motion, touch devices and anything but a tall enough page,
 * where native scrolling is already the better experience.
 * ------------------------------------------------------------------ */

export function useSmoothScroll() {
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (prefersReducedMotion() || isTouchDevice()) return;
    if (!("onscroll" in document.documentElement)) return;

    const root = document.documentElement;
    let target = window.scrollY;
    let current = target;
    let raf = 0;
    let running = false;
    let last = 0;
    // Set while we move the scroller ourselves, so the resulting native
    // `scroll` events are not mistaken for user input.
    let programmatic = false;
    const EASE = 0.11;

    const max = () =>
      Math.max(0, document.documentElement.scrollHeight - window.innerHeight);

    const clamp = (v) => Math.min(max(), Math.max(0, v));

    const start = () => {
      if (running) return;
      running = true;
      last = 0;
      raf = requestAnimationFrame(step);
    };

    const step = (now) => {
      if (!last) last = now;
      const dt = Math.min(64, now - last);
      last = now;
      // Frame-rate independent damping.
      current += (target - current) * (1 - Math.pow(1 - EASE, dt / 16.667));
      if (Math.abs(target - current) < 0.12) {
        current = target;
        programmatic = true;
        window.scrollTo(0, current);
        running = false;
        raf = 0;
        return;
      }
      programmatic = true;
      window.scrollTo(0, current);
      raf = requestAnimationFrame(step);
    };

    // Native scroll we did not initiate: scrollbar drag, find-in-page,
    // focus-driven scrolling, or an anchor jump. Adopt it as the new truth.
    const onScroll = () => {
      if (programmatic) {
        programmatic = false;
        return;
      }
      if (running) {
        running = false;
        if (raf) cancelAnimationFrame(raf);
        raf = 0;
      }
      target = current = window.scrollY;
    };

    const onWheel = (e) => {
      if (e.ctrlKey || e.metaKey) return; // pinch-zoom
      e.preventDefault();
      const delta = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
      if (!running) current = window.scrollY;
      target = clamp(target + delta);
      start();
    };

    const onKey = (e) => {
      const map = {
        ArrowDown: 90,
        ArrowUp: -90,
        PageDown: window.innerHeight * 0.85,
        PageUp: -window.innerHeight * 0.85,
        Home: -max(),
        End: max(),
        " ": window.innerHeight * 0.85,
      };
      if (!(e.key in map)) return;
      if (e.target instanceof HTMLElement && /input|textarea|select/i.test(e.target.tagName)) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      e.preventDefault();
      if (!running) current = window.scrollY;
      target = clamp(target + map[e.key]);
      start();
    };

    const onResize = () => {
      target = clamp(target);
      if (!running) current = clamp(current);
    };

    current = target = window.scrollY;
    root.style.scrollBehavior = "auto";
    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("keydown", onKey);
    window.addEventListener("resize", onResize);

    return () => {
      if (raf) cancelAnimationFrame(raf);
      root.style.scrollBehavior = "";
      window.removeEventListener("wheel", onWheel);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("resize", onResize);
    };
  }, []);
}

/* ------------------------------------------------------------------ *
 * Scroll progress + scrolled-state (rAF-coalesced)
 * ------------------------------------------------------------------ */

export function useScrollState() {
  const [state, setState] = useState({ progress: 0, scrolled: false, y: 0 });
  const ticking = useRef(false);

  useEffect(() => {
    const read = () => {
      ticking.current = false;
      const y = window.scrollY || 0;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      setState({ progress: max > 0 ? Math.min(1, Math.max(0, y / max)) : 0, scrolled: y > 12, y });
    };
    const onScroll = () => {
      if (ticking.current) return;
      ticking.current = true;
      requestAnimationFrame(read);
    };
    read();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  return state;
}

/* ------------------------------------------------------------------ *
 * Scroll-triggered reveal
 * One shared IntersectionObserver for every [data-reveal] in view.
 * Content stays visible if JS or IO is unavailable.
 * ------------------------------------------------------------------ */

let revealObserver = null;
const revealTargets = new WeakMap();

function getRevealObserver() {
  if (revealObserver) return revealObserver;
  revealObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const el = entry.target;
        // `reveal-pending` is intentionally left in place: the stylesheet
        // scopes the hidden state with `:not(.is-revealed)`, so adding the
        // second class is enough to trigger the transition.
        el.classList.add("is-revealed");
        revealObserver.unobserve(el);
      }
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
  );
  return revealObserver;
}

/**
 * Reveal `ref`'s element when it scrolls into view.
 * `stagger` in ms delays it, and `index` auto-computes a per-child stagger.
 */
export function useReveal({ threshold, delay = 0, stagger = 0, index = 0, enabled = true } = {}) {
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || !enabled) return;

    const ms = delay + stagger * index;
    if (ms > 0) el.style.setProperty("--reveal-delay", `${ms}ms`);

    // No motion preference: show immediately, no observer needed.
    if (prefersReducedMotion() || typeof IntersectionObserver === "undefined") {
      el.classList.add("is-revealed");
      return;
    }

    el.classList.add("reveal-pending");
    // Register once per element.
    if (!revealTargets.has(el)) {
      revealTargets.set(el, true);
      getRevealObserver().observe(el);
    }
    return () => {
      /* keep observing; once revealed the observer unobserves itself */
    };
  }, [delay, stagger, index, enabled]);

  return ref;
}

/**
 * Reveals direct children of `ref` as a stagger group.
 * Used for grids and lists so items cascade instead of popping in together.
 */
export function useRevealGroup({ stagger = 70, selector = ":scope > *", enabled = true } = {}) {
  const ref = useRef(null);

  useEffect(() => {
    const root = ref.current;
    if (!root || !enabled) return;

    const kids = Array.from(root.querySelectorAll(selector));
    if (!kids.length) return;

    if (prefersReducedMotion() || typeof IntersectionObserver === "undefined") {
      kids.forEach((k) => k.classList.add("is-revealed"));
      return;
    }

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          kids.forEach((k) => {
            k.classList.add("is-revealed");
            io.unobserve(k);
          });
        });
      },
      { rootMargin: "0px 0px -6% 0px", threshold: 0.05 }
    );

    kids.forEach((k, i) => {
      k.classList.add("reveal-stagger-item");
      k.classList.add("reveal-pending");
      k.style.setProperty("--reveal-delay", `${i * stagger}ms`);
      io.observe(k);
    });

    return () => io.disconnect();
  }, [stagger, selector, enabled]);

  return ref;
}

/* ------------------------------------------------------------------ *
 * Pointer-driven 3D tilt
 * GPU-only (transform), pointer-events based, and fully disabled for
 * touch / reduced-motion / low-power devices.
 * ------------------------------------------------------------------ */

export function useTilt({ max = 9, scale = 1.015, glare = true, enabled = true } = {}) {
  const ref = useRef(null);
  const raf = useRef(0);
  const active = useRef(false);

  const write = useCallback(
    (rx, ry, gx, gy, s) => {
      const el = ref.current;
      if (!el) return;
      el.style.setProperty("--tilt-x", `${rx.toFixed(2)}deg`);
      el.style.setProperty("--tilt-y", `${ry.toFixed(2)}deg`);
      el.style.setProperty("--tilt-gx", `${(gx * 100).toFixed(1)}%`);
      el.style.setProperty("--tilt-gy", `${(gy * 100).toFixed(1)}%`);
      el.style.setProperty("--tilt-scale", s.toFixed(4));
    },
    []
  );

  useEffect(() => {
    const el = ref.current;
    if (!el || !enabled || !motionAllowed()) return;

    const onMove = (e) => {
      if (raf.current) return;
      raf.current = requestAnimationFrame(() => {
        raf.current = 0;
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) return;
        const px = (e.clientX - r.left) / r.width;
        const py = (e.clientY - r.top) / r.height;
        write(
          (0.5 - py) * max * 2,
          (px - 0.5) * max * 2,
          glare ? px : 0.5,
          glare ? py : 0.5,
          scale
        );
      });
    };

    const onEnter = () => {
      active.current = true;
      el.classList.add("is-tilting");
    };

    const onLeave = () => {
      active.current = false;
      el.classList.remove("is-tilting");
      if (raf.current) {
        cancelAnimationFrame(raf.current);
        raf.current = 0;
      }
      write(0, 0, 0.5, 0.5, 1);
    };

    el.addEventListener("pointermove", onMove);
    el.addEventListener("pointerenter", onEnter);
    el.addEventListener("pointerleave", onLeave);

    return () => {
      if (raf.current) cancelAnimationFrame(raf.current);
      el.removeEventListener("pointermove", onMove);
      el.removeEventListener("pointerenter", onEnter);
      el.removeEventListener("pointerleave", onLeave);
    };
  }, [max, scale, glare, enabled, write]);

  return ref;
}

/* ------------------------------------------------------------------ *
 * Delegated pointer glow
 * One passive listener for every glass surface on the page, instead of
 * a hook per card. Sets --mx/--my which the stylesheet uses for the
 * radial highlight and the tilt glare.
 * ------------------------------------------------------------------ */

let glowBound = false;

export function initPointerGlow() {
  if (glowBound || typeof window === "undefined" || !motionAllowed()) return;
  glowBound = true;

  let queued = false;
  let target = null;
  let x = 0;
  let y = 0;

  const flush = () => {
    queued = false;
    if (!target) return;
    const r = target.getBoundingClientRect();
    if (!r.width || !r.height) return;
    target.style.setProperty("--mx", `${(((x - r.left) / r.width) * 100).toFixed(1)}%`);
    target.style.setProperty("--my", `${(((y - r.top) / r.height) * 100).toFixed(1)}%`);
  };

  const onMove = (e) => {
    const el = e.target instanceof Element ? e.target.closest(".card, .feature, .hero-panel, .auth-pills span") : null;
    if (el !== target) {
      target = el;
      if (target) {
        const r = target.getBoundingClientRect();
        target.style.setProperty("--tilt-gx", `${(((e.clientX - r.left) / r.width) * 100).toFixed(1)}%`);
        target.style.setProperty("--tilt-gy", `${(((e.clientY - r.top) / r.height) * 100).toFixed(1)}%`);
      }
    }
    if (!target) return;
    x = e.clientX;
    y = e.clientY;
    if (queued) return;
    queued = true;
    requestAnimationFrame(flush);
  };

  const onLeave = () => {
    target = null;
  };

  window.addEventListener("pointermove", onMove, { passive: true });
  document.addEventListener("pointerleave", onLeave, { passive: true });
}

/* ------------------------------------------------------------------ *
 * Parallax offset for background layers
 * ------------------------------------------------------------------------ */

export function useParallax(strength = 0.12, enabled = true) {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el || !enabled || !motionAllowed()) return;
    let raf = 0;
    let queued = false;
    const update = () => {
      queued = false;
      const r = el.getBoundingClientRect();
      if (!r.height) return;
      // -1 (below fold) .. 1 (above fold)
      const p = (r.top + r.height / 2 - window.innerHeight / 2) / (window.innerHeight / 2 + r.height / 2);
      el.style.setProperty("--parallax-y", `${(p * strength * 100).toFixed(2)}px`);
    };
    const onScroll = () => {
      if (queued) return;
      queued = true;
      raf = requestAnimationFrame(update);
    };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
    return () => {
      if (raf) cancelAnimationFrame(raf);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, [strength, enabled]);
  return ref;
}

/* ------------------------------------------------------------------ *
 * Pointer position within an element, 0..1 — for reactive glows
 * ------------------------------------------------------------------ */

export function usePointerGlow(enabled = true) {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el || !enabled || !motionAllowed()) return;
    let raf = 0;
    let queued = false;
    const move = (e) => {
      if (queued) return;
      queued = true;
      raf = requestAnimationFrame(() => {
        queued = false;
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) return;
        el.style.setProperty("--mx", `${(((e.clientX - r.left) / r.width) * 100).toFixed(1)}%`);
        el.style.setProperty("--my", `${(((e.clientY - r.top) / r.height) * 100).toFixed(1)}%`);
      });
    };
    el.addEventListener("pointermove", move);
    return () => {
      if (raf) cancelAnimationFrame(raf);
      el.removeEventListener("pointermove", move);
    };
  }, [enabled]);
  return ref;
}
