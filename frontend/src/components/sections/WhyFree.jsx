import { motion } from 'framer-motion';
import { X, Check } from 'lucide-react';
import { stagger, fadeUp } from '../../styles/animations';
import './WhyFree.css';

export const WhyFree = ({ t }) => {
  return (
    <section className="why-free" id="por-que-gratis">
      <div className="container">
        <div className="why-grid">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2, margin: '0px 0px -100px 0px' }}
            variants={{ visible: { transition: stagger } }}
          >
            <motion.p className="section-label" variants={fadeUp}>{t.nav_why}</motion.p>
            <motion.h2 className="section-title" variants={fadeUp}>
              {t.why_title}
            </motion.h2>
            <motion.p className="section-desc" variants={fadeUp}>
              {t.why_desc}
            </motion.p>
          </motion.div>

          <motion.div
            className="comparison-grid"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2, margin: '0px 0px -100px 0px' }}
            variants={{ visible: { transition: { staggerChildren: 0.15 } } }}
          >
            <motion.div className="comp-card others" variants={fadeUp} whileHover={{ y: -8, scale: 1.01 }}>
              <div className="comp-card-label">{t.comp_others}</div>
              <ul className="comp-list">
                <li><X size={18} className="comp-icon x" /> {t.comp_1}</li>
                <li><X size={18} className="comp-icon x" /> {t.comp_2}</li>
                <li><X size={18} className="comp-icon x" /> {t.comp_3}</li>
                <li><X size={18} className="comp-icon x" /> {t.comp_4}</li>
                <li><X size={18} className="comp-icon x" /> {t.comp_5}</li>
              </ul>
            </motion.div>

            <motion.div className="comp-card ours" variants={fadeUp} whileHover={{ y: -8, scale: 1.01 }}>
              <div className="comp-card-label">{t.comp_ours}</div>
              <ul className="comp-list">
                <li><Check size={18} className="comp-icon check" /> {t.comp_ours_1}</li>
                <li><Check size={18} className="comp-icon check" /> {t.comp_ours_2}</li>
                <li><Check size={18} className="comp-icon check" /> {t.comp_ours_3}</li>
                <li><Check size={18} className="comp-icon check" /> {t.comp_ours_4}</li>
                <li><Check size={18} className="comp-icon check" /> {t.comp_ours_5}</li>
              </ul>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
