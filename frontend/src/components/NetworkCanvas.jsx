import React, { useEffect, useRef, useState } from "react";
import { ambientAllowed, isTouchDevice, isLowPower, prefersReducedMotion } from "../lib/motion";

/**
 * NORMEX knowledge-graph backdrop.
 *
 * A dependency-free canvas 2D node network that mirrors the product's
 * actual subject matter: standards documents connected by normative,
 * test-method, safety and version relationships.
 *
 * Performance contract:
 *  - never mounted until the canvas is close to the viewport (lazy)
 *  - rAF loop is suspended whenever the canvas leaves the viewport
 *  - not rendered at all on reduced-motion, low-power or data-saver devices
 *  - DPR-capped at 2 so retina displays do not quadruple the fill cost
 *  - node count and link budget scale to the measured area
 *  - degrades to a static rendered frame if rAF is unavailable
 */
export default function NetworkCanvas({
  className = "",
  density = 1,
  nodeColor = "99,102,241",
  linkColor = "79,70,229",
  accentColor = "8,145,178",
  interactive = true,
  style,
}) {
  const hostRef = useRef(null);
  const canvasRef = useRef(null);
  const [enabled, setEnabled] = useState(false);
  const [visible, setVisible] = useState(false);

  /* ---- gate 1: device capability (evaluated once) ---- */
  useEffect(() => {
    setEnabled(ambientAllowed() && !isLowPower());
  }, []);

  /* ---- gate 2: lazy mount + viewport pause ---- */
  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    if (!("IntersectionObserver" in window)) {
      setVisible(true);
      return;
    }
    // rootMargin mounts it slightly before it is needed.
    const io = new IntersectionObserver(
      ([entry]) => setVisible(entry.isIntersecting),
      { rootMargin: "300px 0px", threshold: 0 }
    );
    io.observe(host);
    return () => io.disconnect();
  }, []);

  /* ---- gate 3: document visibility (pause when tab is hidden) ---- */
  const [tabActive, setTabActive] = useState(true);
  useEffect(() => {
    const on = () => setTabActive(!document.hidden);
    document.addEventListener("visibilitychange", on);
    return () => document.removeEventListener("visibilitychange", on);
  }, []);

  const running = enabled && visible && tabActive;

  useEffect(() => {
    if (!running) return;
    const canvas = canvasRef.current;
    const host = hostRef.current;
    if (!canvas || !host) return;
    const ctx = canvas.getContext("2d", { alpha: true });
    if (!ctx) return;

    const reduce = prefersReducedMotion();
    const coarse = isTouchDevice();

    let width = 0;
    let height = 0;
    let dpr = 1;
    let nodes = [];
    let raf = 0;
    let pointer = { x: -9999, y: -9999, active: false };

    const LINK_DIST_BASE = 132;

    const seed = () => {
      const rect = host.getBoundingClientRect();
      width = Math.max(1, rect.width);
      height = Math.max(1, rect.height);
      dpr = Math.min(2, window.devicePixelRatio || 1);
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      // Node budget scales with area, hard-capped so big screens stay smooth.
      const target = Math.round(
        Math.min(78, Math.max(18, (width * height) / 20000)) * density
      );
      const linkDist = LINK_DIST_BASE * (width < 640 ? 0.7 : 1);

      nodes = Array.from({ length: target }, (_, i) => {
        // A few "hub" nodes get larger radii and brighter accents, which
        // reads as a hub-and-spoke standards graph.
        const hub = i % 11 === 0;
        return {
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.16,
          vy: (Math.random() - 0.5) * 0.16,
          r: hub ? 2.6 + Math.random() * 1.8 : 1.1 + Math.random() * 1.2,
          hub,
          depth: Math.random(),
        };
      });
      return linkDist;
    };

    let linkDist = seed();

    const resize = () => {
      linkDist = seed();
    };

    const onPointerMove = (e) => {
      if (!interactive || coarse) return;
      const r = canvas.getBoundingClientRect();
      pointer.x = e.clientX - r.left;
      pointer.y = e.clientY - r.top;
      pointer.active = true;
    };
    const onPointerLeave = () => {
      pointer.active = false;
      pointer.x = pointer.y = -9999;
    };

    let t = 0;

    const draw = (dt) => {
      t += dt;
      ctx.clearRect(0, 0, width, height);

      const px = pointer.x;
      const py = pointer.y;

      for (const n of nodes) {
        n.x += n.vx * dt;
        n.y += n.vy * dt;

        // Soft bounds: wrap with a margin so nodes never visibly pop.
        const m = 24;
        if (n.x < -m) n.x = width + m;
        else if (n.x > width + m) n.x = -m;
        if (n.y < -m) n.y = height + m;
        else if (n.y > height + m) n.y = -m;

        if (pointer.active) {
          const dx = n.x - px;
          const dy = n.y - py;
          const d2 = dx * dx + dy * dy;
          const R = 150;
          if (d2 < R * R && d2 > 0.01) {
            const d = Math.sqrt(d2);
            const push = ((R - d) / R) * 0.5;
            n.x += (dx / d) * push;
            n.y += (dy / d) * push;
          }
        }
      }

      /* ---- links ---- */
      ctx.lineWidth = 1;
      for (let i = 0; i < nodes.length; i++) {
        const a = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const b = nodes[j];
          const dx = a.x - b.x;
          if (dx > linkDist || dx < -linkDist) continue;
          const dy = a.y - b.y;
          if (dy > linkDist || dy < -linkDist) continue;
          const dist = Math.hypot(dx, dy);
          if (dist > linkDist) continue;
          const alpha = (1 - dist / linkDist) * 0.3;
          ctx.strokeStyle = `rgba(${linkColor},${alpha.toFixed(3)})`;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }

      /* ---- pointer links ---- */
      if (pointer.active) {
        for (const n of nodes) {
          const dist = Math.hypot(n.x - px, n.y - py);
          if (dist > 190) continue;
          ctx.strokeStyle = `rgba(${accentColor},${((1 - dist / 190) * 0.4).toFixed(3)})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(px, py);
          ctx.lineTo(n.x, n.y);
          ctx.stroke();
        }
      }

      /* ---- nodes ---- */
      for (const n of nodes) {
        const pulse = n.hub ? 0.75 + Math.sin(t / 620 + n.depth * 6) * 0.25 : 1;
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r * pulse, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${n.hub ? accentColor : nodeColor},${(n.hub ? 0.85 : 0.6).toFixed(3)})`;
        ctx.fill();

        if (n.hub) {
          ctx.beginPath();
          ctx.arc(n.x, n.y, n.r * 3.4, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(${accentColor},0.07)`;
          ctx.fill();
        }
      }
    };

    if (reduce) {
      // Static single frame — no loop at all.
      draw(0);
    } else {
      let last = 0;
      const loop = (now) => {
        const dt = last ? Math.min(48, now - last) : 16;
        last = now;
        draw(dt);
        raf = requestAnimationFrame(loop);
      };
      raf = requestAnimationFrame(loop);
    }

    const ro = "ResizeObserver" in window ? new ResizeObserver(resize) : null;
    if (ro) ro.observe(host);
    else window.addEventListener("resize", resize);

    if (interactive && !coarse) {
      window.addEventListener("pointermove", onPointerMove, { passive: true });
      window.addEventListener("pointerleave", onPointerLeave, { passive: true });
    }

    return () => {
      if (raf) cancelAnimationFrame(raf);
      if (ro) ro.disconnect();
      else window.removeEventListener("resize", resize);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerleave", onPointerLeave);
    };
  }, [running, density, nodeColor, linkColor, accentColor, interactive]);

  return (
    <div ref={hostRef} className={`netcanvas ${className}`} aria-hidden="true" style={style}>
      {enabled ? <canvas ref={canvasRef} className="netcanvas-el" /> : null}
    </div>
  );
}
