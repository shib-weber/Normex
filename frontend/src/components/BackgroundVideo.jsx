import React, { useEffect, useRef, useState } from "react";

/**
 * Decorative background video.
 *
 * The tag is authored with the full autoplay/loop/muted/playsinline set so the
 * browser can start it without user interaction, and `preload="metadata"` keeps
 * the initial transfer small. A `poster` is always supplied so a frame is
 * painted before the first video frame decodes.
 *
 * Beyond markup, playback is actively managed:
 *  - never auto-started under prefers-reduced-motion; the poster stands in
 *  - paused whenever it scrolls out of view
 *  - paused when the tab is hidden
 *  - skipped entirely on save-data / 2G, where the poster is used instead
 */
export default function BackgroundVideo({ src, poster, className = "", children, ...rest }) {
  const videoRef = useRef(null);
  const [posterOnly, setPosterOnly] = useState(false);

  useEffect(() => {
    const conn = navigator.connection;
    const slow = conn && (conn.saveData || /2g/.test(conn.effectiveType || ""));
    if (slow || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setPosterOnly(true);
    }
  }, []);

  useEffect(() => {
    if (posterOnly) return;
    const el = videoRef.current;
    if (!el) return;

    let visible = true;
    let tabActive = !document.hidden;

    const sync = () => {
      if (visible && tabActive) {
        const p = el.play();
        if (p && typeof p.catch === "function") p.catch(() => {});
      } else if (!el.paused) {
        el.pause();
      }
    };

    let io = null;
    if ("IntersectionObserver" in window) {
      io = new IntersectionObserver(
        ([entry]) => {
          visible = entry.isIntersecting;
          sync();
        },
        { threshold: 0.01 }
      );
      io.observe(el);
    }

    const onVisibility = () => {
      tabActive = !document.hidden;
      sync();
    };
    document.addEventListener("visibilitychange", onVisibility);

    return () => {
      if (io) io.disconnect();
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [posterOnly]);

  return (
    <div className={`hero-video-bg ${className}`} aria-hidden="true" {...rest}>
      {posterOnly ? (
        <div
          className="hero-video-poster"
          style={poster ? { backgroundImage: `url(${poster})` } : undefined}
        />
      ) : (
        <video
          ref={videoRef}
          poster={poster}
          autoPlay
          muted
          loop
          playsInline
          preload="metadata"
          disablePictureInPicture
          tabIndex={-1}
        >
          <source src={src} type="video/mp4" />
        </video>
      )}
      {children}
    </div>
  );
}
