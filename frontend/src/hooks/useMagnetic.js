import { useState, useEffect, useRef, useCallback } from 'react';

export const useMagnetic = (ref, strength = 0.25) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const targetPos = useRef({ x: 0, y: 0 });
  const currentPos = useRef({ x: 0, y: 0 });
  const rafId = useRef(null);
  const ACTIVATION_RADIUS = 140;
  const LERP_FACTOR = 0.1;

  const animate = useCallback(() => {
    const dx = targetPos.current.x - currentPos.current.x;
    const dy = targetPos.current.y - currentPos.current.y;

    if (Math.abs(dx) > 0.01 || Math.abs(dy) > 0.01) {
      currentPos.current.x += dx * LERP_FACTOR;
      currentPos.current.y += dy * LERP_FACTOR;
      setPosition({ x: currentPos.current.x, y: currentPos.current.y });
    }

    rafId.current = requestAnimationFrame(animate);
  }, []);

  useEffect(() => {
    rafId.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafId.current);
  }, [animate]);

  const handleMouseMove = useCallback((e) => {
    if (!ref.current) return;

    const { clientX, clientY } = e;
    const { left, top, width, height } = ref.current.getBoundingClientRect();

    const centerX = left + width / 2;
    const centerY = top + height / 2;

    const deltaX = clientX - centerX;
    const deltaY = clientY - centerY;

    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
    if (distance < ACTIVATION_RADIUS) {
      const falloff = 1 - distance / ACTIVATION_RADIUS;
      targetPos.current = {
        x: deltaX * strength * falloff,
        y: deltaY * strength * falloff,
      };
    } else {
      targetPos.current = { x: 0, y: 0 };
    }
  }, [ref, strength]);

  const handleMouseLeave = useCallback(() => {
    targetPos.current = { x: 0, y: 0 };
  }, []);

  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [handleMouseMove]);

  return { x: position.x, y: position.y, handleMouseLeave };
};
