export const transitionVariants = {
  enter: ({ direction, actionType }) => {
    if (actionType === 'paginate') {
      return { 
        x: direction > 0 ? '100%' : '-100%',
        rotateY: direction > 0 ? 45 : -45, 
        opacity: 0, 
        scale: 0.95,
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
  center: {
    x: 0,
    rotateY: 0.01,
    opacity: 1,
    scale: 1,
    transition: { 
      type: 'spring',
      stiffness: 140,
      damping: 26,
      restDelta: 0.001
    }
  },
  exit: ({ direction, actionType }) => {
    if (actionType === 'paginate') {
      return { 
        x: direction < 0 ? '100%' : '-100%',
        rotateY: direction < 0 ? -45 : 45,
        opacity: 0, 
        scale: 0.95,
        transition: { duration: 0.3, ease: 'easeIn' }
      }
    } else {
      return { 
        rotateY: direction > 0 ? -90 : 90,
        opacity: 0,
        transformOrigin: direction > 0 ? 'right center' : 'left center',
        scale: 0.9,
        transition: { duration: 0.35, ease: 'easeInOut' }
      }
    }
  }
};

export const sideVariants = {
  enter: (custom) => ({
    x: custom.direction > 0 ? 50 : -50,
    opacity: 0,
    rotateY: 0
  }),
  center: {
    x: 0,
    opacity: 1,
    rotateY: 0,
    width: '100%',
    height: '100%',
    transition: {
      duration: 0.3,
      ease: 'easeOut'
    }
  },
  exit: (custom) => ({
    x: custom.direction > 0 ? -50 : 50,
    opacity: 0,
    rotateY: 0,
    transition: {
      duration: 0.2,
      ease: 'easeIn'
    }
  }
)};
