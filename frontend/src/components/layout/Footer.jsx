import './Footer.css';
import { useLanguage } from '../../contexts/LanguageContext';
import { Link } from 'react-router-dom';
import { FileText } from 'lucide-react';
import { motion } from 'framer-motion';

export const Footer = ({ scrollToHero }) => {
  const { t } = useLanguage();
  const currentYear = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-logo">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', userSelect: 'none' }}>
              <FileText size={20} color="#ef4444" />
              <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-heading)' }}>
                Layr
                <Link 
                  to="/" 
                  onClick={(e) => { e.preventDefault(); scrollToHero(); }}
                  style={{ textDecoration: 'none', color: 'inherit', display: 'flex', alignItems: 'center' }}
                >
                  <motion.span 
                    style={{ color: 'var(--accent-rose)', display: 'inline-block', cursor: 'pointer' }}
                    whileHover={{ 
                      y: -4,
                      scale: 1.1,
                      rotate: [0, -10, 10, -10, 0],
                    }}
                    transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                  >
                    PDF
                  </motion.span>
                </Link>
              </div>
            </div>
          </div>

          <div className="footer-links">
            <Link to="/sobre" className="footer-link">{t.nav_about || 'Sobre'}</Link>
            <Link to="/faq" className="footer-link">{t.nav_faq || 'FAQ'}</Link>
            <a href="https://github.com/OtavioB9/LayrPDF" target="_blank" rel="noopener noreferrer" className="footer-link">GitHub</a>
          </div>
        </div>

        <div className="footer-bottom">
          <p className="footer-copy">
            &copy; {currentYear} LayrPDF. {t.footer_copy || 'Projeto open-source para tradução de PDFs.'}
          </p>
        </div>
      </div>
    </footer>
  );
};
