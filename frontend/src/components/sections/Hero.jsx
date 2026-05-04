import { motion } from 'framer-motion';
import { CheckCircle, ArrowRight } from 'lucide-react';
import { stagger, fadeUp, spring } from '../../styles/animations';
import HeroAnimation from './HeroAnimation';
import './Hero.css';

export const Hero = ({ t, siteLang, scrollToApp, heroRef }) => {
  return (
    <section className="hero" ref={heroRef}>
      <div className="container">
        <div className="hero-grid">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={{ visible: { transition: stagger } }}
          >
            <motion.div variants={fadeUp}>
              <span className="hero-badge">
                <CheckCircle size={14} /> {t.hero_badge}
              </span>
            </motion.div>

            <motion.h1 variants={fadeUp}>
              LayrPDF
            </motion.h1>

            <motion.p className="hero-subtitle" variants={fadeUp}>
              {t.hero_sub_1}<br />
              {t.hero_sub_2}<br />
              {t.hero_sub_3}
            </motion.p>

            <motion.div className="hero-actions" variants={fadeUp}>
              <motion.button 
                className="btn-dark" 
                onClick={scrollToApp}
                whileHover={{ y: -2, boxShadow: '0 8px 30px rgba(239, 68, 68, 0.2)' }}
                whileTap={{ scale: 0.98 }}
              >
                {t.hero_btn_start} <ArrowRight size={18} />
              </motion.button>
              <motion.a 
                href="#como-funciona" 
                className="btn-ghost"
                whileHover={{ border: '1px solid var(--text-heading)' }}
                whileTap={{ scale: 0.98 }}
              >
                {t.hero_btn_more}
              </motion.a>
            </motion.div>
          </motion.div>

          <motion.div
            className="hero-visual"
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ ...spring, delay: 0.3 }}
          >
            <HeroAnimation siteLang={siteLang} />
          </motion.div>
        </div>
      </div>
    </section>
  );
};
