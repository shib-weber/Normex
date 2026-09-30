import React, { useEffect, useRef, useState } from "react";
import { useScrollState, useParallax, useRevealGroup, useReveal } from "../lib/motion";
import NetworkCanvas from "./NetworkCanvas";

/**
 * Slim glassmorphic reading-progress bar pinned to the top of the viewport.
 * Driven by a rAF-coalesced scroll listener, so it never blocks scrolling.
 * `aria-hidden` because it is decorative and duplicates native scroll info.
 */
export function ScrollProgress() {
  const { progress, scrolled } = useScrollState();
  return (
    <div
      className={`scroll-progress ${scrolled ? "is-active" : ""}`}
      aria-hidden="true"
    >
      <span className="scroll-progress-fill" style={{ transform: `scaleX(${progress})` }} />
    </div>
  );
}

/**
 * Fixed ambient layer: soft colour fields plus the knowledge-graph canvas.
 * Purely decorative, sits behind all content, never intercepts pointer events.
 */
export function AmbientField({ variant = "app", showCanvas = true }) {
  return (
    <div className={`ambient ambient-${variant}`} aria-hidden="true">
      <span className="ambient-orb ambient-orb-a" />
      <span className="ambient-orb ambient-orb-b" />
      <span className="ambient-orb ambient-orb-c" />
      <span className="ambient-grid" />
      {showCanvas ? (
        <NetworkCanvas className="ambient-canvas" density={variant === "hero" ? 1.15 : 0.55} />
      ) : null}
    </div>
  );
}

/** Fades + lifts its children into view on scroll. */
export function Reveal({ as: Tag = "div", delay = 0, stagger = 0, index = 0, className = "", style, children, ...rest }) {
  const ref = useReveal({ delay, stagger, index });
  return (
    <Tag ref={ref} className={`reveal ${className}`} style={style} {...rest}>
      {children}
    </Tag>
  );
}

/** Staggers direct children into view. */
export function RevealGroup({
  as: Tag = "div",
  stagger = 70,
  selector = ":scope > *",
  className = "",
  style,
  children,
  ...rest
}) {
  const ref = useRevealGroup({ stagger, selector });
  return (
    <Tag ref={ref} className={`reveal-group ${className}`} style={style} {...rest}>
      {children}
    </Tag>
  );
}

/** Adds a slow parallax drift to its child. */
export function Parallax({ strength = 0.1, className = "", style, children, ...rest }) {
  const ref = useParallax(strength);
  return (
    <div ref={ref} className={`parallax ${className}`} style={style} {...rest}>
      {children}
    </div>
  );
}

/** Count-up number that animates once when scrolled into view. */
export function CountUp({ value, duration = 900, className = "" }) {
  const hostRef = useRef(null);
  const numeric = typeof value === "number" ? value : Number(value);
  const isNumeric = Number.isFinite(numeric) && value !== null && value !== undefined && value !== "";
  const format = (v) =>
    Number.isInteger(numeric) ? String(Math.round(v)) : v.toFixed(1).replace(/\.0$/, "");

  const [display, setDisplay] = useState(() => (isNumeric ? format(numeric) : String(value ?? "")));
  const done = useRef(false);

  useEffect(() => {
    // Non-numeric values (e.g. "—", "Not calculated") are shown verbatim.
    if (!isNumeric) {
      setDisplay(String(value ?? ""));
      return;
    }
    setDisplay(format(numeric));

    const reduce = typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;

    const run = () => {
      if (done.current) return;
      done.current = true;
      const start = performance.now();
      const step = (now) => {
        const p = Math.min(1, (now - start) / duration);
        // easeOutExpo
        const e = p === 1 ? 1 : 1 - Math.pow(2, -10 * p);
        setDisplay(format(numeric * e));
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };

    const host = hostRef.current;
    if (!host || !("IntersectionObserver" in window)) return;
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          run();
          io.disconnect();
        }
      },
      { threshold: 0.4 }
    );
    io.observe(host);
    return () => io.disconnect();
  }, [value, duration, isNumeric, numeric]);

  return (
    <span ref={hostRef} className={className}>
      {display}
    </span>
  );
}
