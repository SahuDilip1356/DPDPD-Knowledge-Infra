import React, { useEffect, useRef } from "react";

const randomBetween = (min, max) => Math.random() * (max - min) + min;

function makeComet({ width, height }) {
  const hue = Math.random() < 0.72 ? 31 : 212;
  const speed = randomBetween(1.5, 4.1);
  const angle = randomBetween(-0.35, 0.35);
  const vx = Math.sin(angle) * speed * randomBetween(0.15, 0.75);
  const vy = Math.cos(angle) * speed;
  return {
    x: randomBetween(width * -0.2, width * 1.2),
    y: randomBetween(-height * 0.6, 0),
    vx,
    vy,
    life: 0,
    maxLife: randomBetween(260, 620),
    length: randomBetween(150, 460),
    width: randomBetween(1.0, 2.2),
    hue,
    sat: randomBetween(72, 92),
    light: randomBetween(56, 78),
    alpha: randomBetween(0.18, 0.55)
  };
}

function drawStaticSky(ctx, width, height) {
  const r1 = Math.max(width, height) * 0.55;
  const glow = ctx.createRadialGradient(width * 0.2, height * 0.12, 0, width * 0.2, height * 0.12, r1);
  glow.addColorStop(0, "rgba(255, 148, 50, 0.26)");
  glow.addColorStop(0.45, "rgba(255, 148, 50, 0.14)");
  glow.addColorStop(1, "rgba(15, 23, 42, 0)");
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, width, height);

  const glow2 = ctx.createRadialGradient(width * 0.75, height * 0.85, 0, width * 0.75, height * 0.85, r1 * 0.9);
  glow2.addColorStop(0, "rgba(33, 100, 196, 0.2)");
  glow2.addColorStop(0.45, "rgba(33, 100, 196, 0.1)");
  glow2.addColorStop(1, "rgba(15, 23, 42, 0)");
  ctx.fillStyle = glow2;
  ctx.fillRect(0, 0, width, height);
}

export default function CometCascadeHeroBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let raf = 0;
    let running = true;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    const resize = () => {
      const { width, height } = canvas.getBoundingClientRect();
      const scale = window.devicePixelRatio || 1;
      canvas.width = Math.floor(width * scale);
      canvas.height = Math.floor(height * scale);
      ctx.setTransform(scale, 0, 0, scale, 0, 0);
      return { width, height };
    };

    let size = resize();
    let comets = Array.from({ length: Math.max(24, Math.floor((size.width * size.height) / 14000)) }, () =>
      makeComet({ width: size.width, height: size.height })
    );

    const render = () => {
      if (!running) return;
      const { width, height } = size;
      ctx.clearRect(0, 0, width, height);
      drawStaticSky(ctx, width, height);

      if (!reduceMotion.matches) {
        comets.forEach((c) => {
          const tailX = c.x - c.vx * (c.length * 0.6);
          const tailY = c.y - c.vy * (c.length * 0.6);
          const grad = ctx.createLinearGradient(c.x, c.y, tailX, tailY);
          const t = Math.min(c.life / c.maxLife, 1);
          const fade = c.alpha * (1 - t * 0.62);

          grad.addColorStop(0, `hsla(${c.hue}, ${c.sat}%, ${c.light + 7}%, ${fade})`);
          grad.addColorStop(0.28, `hsla(${c.hue}, ${c.sat}%, ${c.light - 4}%, ${fade * 0.48})`);
          grad.addColorStop(1, `hsla(${c.hue}, ${c.sat}%, ${c.light - 16}%, 0)`);

          ctx.strokeStyle = grad;
          ctx.lineWidth = c.width;
          ctx.lineCap = "round";
          ctx.beginPath();
          ctx.moveTo(tailX, tailY);
          ctx.lineTo(c.x, c.y);
          ctx.stroke();

          const head = `hsla(${c.hue}, ${c.sat + 14}%, ${Math.min(c.light + 14, 90)}%, ${Math.min(fade * 2.4, 0.9)})`;
          ctx.fillStyle = head;
          ctx.beginPath();
          ctx.arc(c.x, c.y, Math.max(c.width * 1.8, 1.5), 0, Math.PI * 2);
          ctx.fill();

          c.x += c.vx;
          c.y += c.vy;
          c.life += 1;

          if (c.life > c.maxLife || c.x < -120 || c.x > width + 120 || c.y > height + 120) {
            Object.assign(c, makeComet(size));
          }
        });
      }

      ctx.fillStyle = "rgba(255, 255, 255, 0.05)";
      for (let i = 0; i < 8; i++) {
        const x = (i * 17) % width;
        const y = ((i * 43) % height);
        ctx.fillRect(x, y, 1, 1);
      }

      raf = window.requestAnimationFrame(render);
    };

    const onResize = () => {
      size = resize();
      comets = Array.from({ length: Math.max(20, Math.floor((size.width * size.height) / 14000)) }, () =>
        makeComet(size)
      );
      if (!running) return;
      render();
    };

    const onReduceMotionChange = () => {
      drawStaticSky(ctx, size.width, size.height);
    };

    reduceMotion.addEventListener?.("change", onReduceMotionChange);
    window.addEventListener("resize", onResize);
    raf = window.requestAnimationFrame(render);

    return () => {
      running = false;
      window.cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
      reduceMotion.removeEventListener?.("change", onReduceMotionChange);
    };
  }, []);

  return (
    <div className="hero-canvas-wrap" aria-hidden="true">
      <canvas className="hero-canvas" ref={canvasRef} />
    </div>
  );
}

