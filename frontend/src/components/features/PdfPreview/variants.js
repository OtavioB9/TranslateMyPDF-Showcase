export const transitionVariants = {
  enter: ({ direction, actionType, isMobile }) => {
    if (isMobile) {
      return { x: direction > 0 ? 20 : -20, opacity: 0 }
    }
    if (actionType === 'paginate') {
      return { 
        x: direction > 0 ? '100%' : '-100%',
        rotateY: direction > 0 ? 45 : -45, 
        opacity: 0, 
        scale: 0.9,
      }
    } else {
      return { 
        rotateY: direction > 0 ? 90 : -90,
        opacity: 0,
        transformOrigin: direction > 0 ? 'left center' : 'right center',
        scale: 0.9
      }
    }
  },
  center: ({ isMobile }) => ({
    x: 0,
    rotateY: 0,
    opacity: 1,
    scale: 1,
    filter: 'blur(0px)',
    transformOrigin: 'center center',
    transition: isMobile 
      ? { duration: 0.15, ease: 'easeOut' }
      : { type: 'spring', stiffness: 100, damping: 22, mass: 1 }
  }),
  exit: ({ direction, actionType, isMobile }) => {
    if (isMobile) {
      return { x: direction < 0 ? 20 : -20, opacity: 0, transition: { duration: 0.1 } }
    }
    if (actionType === 'paginate') {
      return { 
        x: direction < 0 ? '100%' : '-100%',
        rotateY: direction < 0 ? 45 : -45, 
        opacity: 0, 
        scale: 0.9,
        transition: { duration: 0.3, ease: 'easeIn' }
      }
    } else {
      return { 
        rotateY: direction > 0 ? -90 : 90,
        opacity: 0,
        transformOrigin: direction > 0 ? 'right center' : 'left center',
        scale: 0.9,
        transition: { duration: 0.4, ease: 'easeInOut' }
      }
    }
  }
};

export const sideVariants = {
  enter: (custom) => ({
    x: custom.isMobile ? (custom.direction > 0 ? 20 : -20) : (custom.direction > 0 ? 50 : -50),
    opacity: 0,
    rotateY: 0
  }),
  center: (custom) => ({
    x: 0,
    opacity: 1,
    rotateY: 0,
    width: '100%',
    height: '100%',
    transition: {
      duration: custom.isMobile ? 0.15 : 0.3,
      ease: 'easeOut'
    }
  }),
  exit: (custom) => ({
    x: custom.isMobile ? (custom.direction > 0 ? -20 : 20) : (custom.direction > 0 ? -50 : 50),
    opacity: 0,
    rotateY: 0,
    transition: {
      duration: custom.isMobile ? 0.1 : 0.2,
      ease: 'easeIn'
    }
  })
};
