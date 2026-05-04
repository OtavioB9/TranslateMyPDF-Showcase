import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '../contexts/LanguageContext';
import { useState } from 'react';
import { Plus, Minus } from 'lucide-react';
import './FAQ.css';

export default function FAQ() {
  const { t } = useLanguage();
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    { q: t.faq_q1, a: t.faq_a1 },
    { q: t.faq_q2, a: t.faq_a2 },
    { q: t.faq_q3, a: t.faq_a3 },
    { q: t.faq_q4, a: t.faq_a4 },
    { q: t.faq_q5, a: t.faq_a5 }
  ];

  const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="container faq-container">
      <motion.div 
        initial="hidden" 
        animate="visible" 
        variants={{ visible: { transition: { staggerChildren: 0.1 } } }}
      >
        <motion.p className="section-label" variants={fadeUp}>{t.nav_faq}</motion.p>
        <motion.h1 className="section-title faq-title" variants={fadeUp}>
          {t.faq_title_1} <br /><span>{t.faq_title_2}</span>
        </motion.h1>

        <div className="faq-list">
          {faqs.map((faq, i) => (
            <motion.div 
              key={i}
              className="liquid-glass faq-item"
              variants={fadeUp}
              whileHover={{ y: -4 }}
              transition={{ duration: 0.1, ease: "linear" }}
              onClick={() => setOpenIndex(openIndex === i ? null : i)}
            >
              <div className="faq-question">
                <h3>{faq.q}</h3>
                <div className="faq-icon">
                  {openIndex === i ? <Minus size={20} /> : <Plus size={20} />}
                </div>
              </div>
              <AnimatePresence>
                {openIndex === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                  >
                    <div className="faq-answer">
                      {faq.a}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
