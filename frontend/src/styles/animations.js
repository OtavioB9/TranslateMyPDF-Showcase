export const spring = { 
  type: 'spring', 
  stiffness: 80, 
  damping: 20,
  mass: 1 
};

export const transitionSmooth = {
  duration: 0.8,
  ease: [0.16, 1, 0.3, 1] // Custom cubic-bezier for "Apple-like" feel
};

export const stagger = { staggerChildren: 0.15 };

export const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: transitionSmooth
  },
};
