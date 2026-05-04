import { motion } from 'framer-motion';
import { Globe, Monitor, Smartphone, Check, Info, Zap, HardDrive, Download, Apple, ArrowRight } from 'lucide-react';
import { stagger, fadeUp } from '../../styles/animations';
import './Downloads.css';

export const Downloads = ({ t, scrollToApp }) => {
  return (
    <section className="download-section" id="download">
      <div className="container">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2, margin: '0px 0px -100px 0px' }}
          variants={{ visible: { transition: stagger } }}
        >
          <motion.p className="section-label" variants={fadeUp}>{t.nav_dl}</motion.p>
          <motion.h2 className="section-title" variants={fadeUp}>
            {t.dl_title}
          </motion.h2>
          <motion.p className="section-desc" variants={fadeUp}>
            {t.dl_desc}
          </motion.p>
        </motion.div>

        <motion.div
          className="download-grid"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2, margin: '0px 0px -100px 0px' }}
          variants={{ visible: { transition: { staggerChildren: 0.15 } } }}
        >
          <motion.div className="download-card" variants={fadeUp} whileHover={{ y: -12, scale: 1.02 }}>
            <span className="download-card-badge live">{t.dl_avail}</span>
            <h3><Globe size={18} style={{ verticalAlign: '-3px', marginRight: '0.4rem' }} />{t.dl_web}</h3>
            <p>{t.dl_web_desc}</p>
            <ul className="spec-list">
              <li><Check size={14} /> {t.dl_f1}</li>
              <li><Check size={14} /> {t.dl_f2}</li>
              <li><Info size={14} /> {t.dl_f3}</li>
            </ul>
            <button className="btn-dark" style={{ width: '100%', justifyContent: 'center' }} onClick={scrollToApp}>
              {t.nav_cta} <ArrowRight size={16} />
            </button>
          </motion.div>

          <motion.div className="download-card featured" variants={fadeUp} whileHover={{ y: -12, scale: 1.02 }}>
            <h3><Monitor size={18} style={{ verticalAlign: '-3px', marginRight: '0.4rem' }} />{t.dl_desk_title}</h3>
            <p>{t.dl_desk_desc2}</p>
            <ul className="spec-list">
              <li><Zap size={14} /> {t.dl_f6}</li>
              <li><HardDrive size={14} /> {t.dl_f7}</li>
              <li><Download size={14} /> {t.dl_f8}</li>
            </ul>
            <span className="btn-disabled">{t.dl_dev}</span>
          </motion.div>

          <motion.div className="download-card" variants={fadeUp} whileHover={{ y: -12, scale: 1.02 }}>
            <h3><Smartphone size={18} style={{ verticalAlign: '-3px', marginRight: '0.4rem' }} />{t.dl_mobile_title}</h3>
            <p>{t.dl_mobile_desc}</p>
            <ul className="spec-list">
              <li><Apple size={14} /> {t.dl_f9}</li>
              <li><Smartphone size={14} /> {t.dl_f10}</li>
              <li><Zap size={14} /> {t.dl_f11}</li>
            </ul>
            <span className="btn-disabled">{t.dl_soon}</span>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};
