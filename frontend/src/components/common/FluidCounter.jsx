import { useEffect, useRef } from 'react';
import { useSpring, useTransform } from 'framer-motion';

export const FluidCounter = ({ value }) => {
  const springValue = useSpring(value, { stiffness: 25, damping: 15, mass: 1 });
  const display = useTransform(springValue, (latest) => Math.round(latest));
  const ref = useRef(null);

  useEffect(() => {
    springValue.set(value);
  }, [value, springValue]);

  useEffect(() => {
    return display.on("change", (latest) => {
      if (ref.current) {
        ref.current.textContent = Math.round(latest);
      }
    });
  }, [display]);

  return <span ref={ref}>{Math.round(value)}</span>;
};
