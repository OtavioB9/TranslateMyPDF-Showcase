import { motion } from 'framer-motion';
import { useLanguage } from '../contexts/LanguageContext';
import { ShieldCheck, Globe, Zap, Heart, Layout, Maximize } from 'lucide-react';
import './About.css';

export default function About() {
  const { t } = useLanguage();

  const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 }
  };

  const features = [
    { icon: <Zap size={24} />, title: t.about_feat_1_title, desc: t.about_feat_1_desc },
    { icon: <Globe size={24} />, title: t.about_feat_2_title, desc: t.about_feat_2_desc },
    { icon: <ShieldCheck size={24} />, title: t.about_feat_3_title, desc: t.about_feat_3_desc },
    { icon: <Layout size={24} />, title: t.about_feat_5_title, desc: t.about_feat_5_desc },
    { icon: <Maximize size={24} />, title: t.about_feat_6_title, desc: t.about_feat_6_desc },
    { icon: <Heart size={24} />, title: t.about_feat_4_title, desc: t.about_feat_4_desc }
  ];

  return (
    <div className="container about-container">
      <motion.div 
        initial="hidden" 
        animate="visible" 
        variants={{ visible: { transition: { staggerChildren: 0.1 } } }}
      >
        <motion.p className="section-label" variants={fadeUp} transition={{ duration: 0.6 }}>{t.about_label}</motion.p>
        <motion.h1 className="section-title about-title" variants={fadeUp} transition={{ duration: 0.6 }}>
          {t.about_title_1} <br /><span>{t.about_title_2}</span>
        </motion.h1>
        
        <motion.p className="section-desc about-desc" variants={fadeUp} transition={{ duration: 0.6 }}>
          {t.about_desc}
        </motion.p>

        <div className="about-features-grid">
          {features.map((item, i) => (
            <motion.div 
              key={i}
              className="liquid-glass about-feature-card" 
              variants={fadeUp}
              whileHover={{ y: -8, scale: 1.02 }}
              transition={{ duration: 0.1, ease: "linear" }}
            >
              <div className="about-feature-icon">
                {item.icon}
              </div>
              <h3>{item.title}</h3>
              <p>{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
