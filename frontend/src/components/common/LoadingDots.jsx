import { motion } from 'framer-motion';

export const LoadingDots = () => {
  return (
    <motion.span style={{ display: 'inline-flex', marginLeft: '4px' }}>
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0.2 }}
          animate={{ opacity: 1 }}
          transition={{
            repeat: Infinity,
            duration: 0.6,
            repeatType: "mirror",
            delay: i * 0.2
          }}
        >
          .
        </motion.span>
      ))}
    </motion.span>
  );
};
