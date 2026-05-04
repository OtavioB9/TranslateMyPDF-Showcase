import { motion } from 'framer-motion';
import { Info } from 'lucide-react';
import { fadeUp } from '../../styles/animations';
import './HowItWorks.css';

export const HowItWorks = ({ t }) => {
  return (
    <section className="how-it-works" id="como-funciona">
      <div className="container">
        <motion.div 
          className="section-header"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2, margin: '0px 0px -100px 0px' }}
          variants={{ visible: { transition: { staggerChildren: 0.1 } } }}
        >
          <motion.p className="section-label" variants={fadeUp}>{t.nav_how}</motion.p>
          <motion.h2 className="section-title" variants={fadeUp}>
            {t.how_title}
          </motion.h2>
          <motion.p className="section-desc" variants={fadeUp}>
            {t.how_desc}
          </motion.p>
        </motion.div>

        <motion.div
          className="steps-grid"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={{ visible: { transition: { staggerChildren: 0.2 } } }}
        >
          <motion.div className="step-card" variants={fadeUp} whileHover={{ y: -10, scale: 1.02 }} transition={{ duration: 0.1, ease: "linear" }}>
            <div className="step-number">01</div>
            <h3>{t.step_1_title}</h3>
            <p>{t.step_1_desc}</p>
          </motion.div>
          <motion.div className="step-card" variants={fadeUp} whileHover={{ y: -10, scale: 1.02 }} transition={{ duration: 0.1, ease: "linear" }}>
            <div className="step-number">02</div>
            <h3>{t.step_2_title}</h3>
            <p>{t.step_2_desc}</p>
          </motion.div>
          <motion.div className="step-card" variants={fadeUp} whileHover={{ y: -10, scale: 1.02 }} transition={{ duration: 0.1, ease: "linear" }}>
            <div className="step-number">03</div>
            <h3>{t.step_3_title}</h3>
            <p>{t.step_3_desc}</p>
          </motion.div>
        </motion.div>

        <motion.div 
          className="info-banner"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <Info size={18} className="info-banner-icon" />
          <p>
            <strong>{t.info_web}</strong> {t.info_web_desc} <strong>{t.info_desk}</strong> {t.info_desk_desc}
          </p>
        </motion.div>
      </div>
    </section>
  );
};
