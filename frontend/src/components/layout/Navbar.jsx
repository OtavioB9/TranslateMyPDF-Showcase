import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { FileText, Sun, Moon, Menu, X, ChevronRight } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTheme } from '../../contexts/ThemeContext';
import './Navbar.css';

export default function Navbar({ scrollToApp, scrollToHero }) {
  const { t, siteLang, setSiteLang } = useLanguage();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  const isHome = location.pathname === '/';

  useEffect(() => {
    setIsOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const fadeUp = {
    hidden: { opacity: 0, y: -20 },
    visible: { opacity: 1, y: 0 }
  };

  const handleNavClick = (e, href) => {
    if (href.startsWith('#')) {
      if (!isHome) {
        e.preventDefault();
        navigate('/', { state: { scrollTo: href } });
      }
    }
  };

  const handleLogoClick = (e) => {
    if (isHome) {
      e.preventDefault();
      scrollToHero();
    }
  };

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <motion.div
          whileHover={{ y: -4 }}
          transition={{ type: 'spring', stiffness: 400, damping: 25 }}
        >
          <Link to="/" className="nav-brand" onClick={handleLogoClick} style={{ textDecoration: 'none' }}>
            <div className="nav-brand-icon">
              <FileText size={18} />
            </div>
            <span className="nav-brand-text">LayrPDF</span>
          </Link>
        </motion.div>

        <div className="nav-right">
          <motion.div 
            className="nav-links" 
            variants={{ visible: { transition: { staggerChildren: 0.1 } } }} 
            initial="hidden" 
            animate="visible"
          >
            <motion.a 
              href="#como-funciona" 
              className="nav-link" 
              variants={fadeUp} 
              onClick={(e) => handleNavClick(e, '#como-funciona')}
              whileHover={{ y: -5 }}
              style={{ textDecoration: 'none' }}
            >
              {t.nav_how}
            </motion.a>
            <motion.a 
              href="#por-que-gratis" 
              className="nav-link" 
              variants={fadeUp} 
              onClick={(e) => handleNavClick(e, '#por-que-gratis')}
              whileHover={{ y: -5 }}
              style={{ textDecoration: 'none' }}
            >
              {t.nav_why}
            </motion.a>
            
            <Link 
              to="/sobre" 
              className={`nav-link ${location.pathname === '/sobre' ? 'active' : ''}`}
              style={{ textDecoration: 'none' }}
            >
              <motion.span variants={fadeUp} whileHover={{ y: -5 }} style={{ display: 'inline-block' }}>
                {t.nav_about}
              </motion.span>
            </Link>

            <Link 
              to="/faq" 
              className={`nav-link ${location.pathname === '/faq' ? 'active' : ''}`}
              style={{ textDecoration: 'none' }}
            >
              <motion.span variants={fadeUp} whileHover={{ y: -5 }} style={{ display: 'inline-block' }}>
                {t.nav_faq}
              </motion.span>
            </Link>

            <motion.a 
              href="#download" 
              className="nav-link" 
              variants={fadeUp} 
              onClick={(e) => handleNavClick(e, '#download')}
              whileHover={{ y: -5 }}
              style={{ textDecoration: 'none' }}
            >
              {t.nav_dl}
            </motion.a>
          </motion.div>
          
          <motion.div 
            className="nav-actions" 
            variants={{ visible: { transition: { staggerChildren: 0.1, delayChildren: 0.2 } } }} 
            initial="hidden" 
            animate="visible"
          >
            <motion.button 
              className="nav-cta" 
              onClick={() => isHome ? scrollToApp() : navigate('/')}
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              variants={fadeUp}
            >
              {t.nav_cta}
            </motion.button>

            <motion.button 
              className="theme-toggle lang-btn" 
              onClick={() => setSiteLang(siteLang === 'pt' ? 'en' : 'pt')} 
              style={{ fontSize: '0.8rem', fontWeight: 700 }}
              whileHover={{ backgroundColor: 'var(--accent-rose-soft)', y: -5 }}
              whileTap={{ scale: 0.9 }}
              variants={fadeUp}
              aria-label={siteLang === 'pt' ? 'Switch to English' : 'Mudar para Português'}
            >
              {siteLang === 'pt' ? 'EN' : 'PT-BR'}
            </motion.button>
            
            <motion.button 
              className="theme-toggle" 
              onClick={toggleTheme} 
              whileHover={{ rotate: 15, y: -5 }}
              whileTap={{ scale: 0.9 }}
              variants={fadeUp}
              aria-label={theme === 'dark' ? 'Ativar modo claro' : 'Ativar modo escuro'}
            >
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            </motion.button>
          </motion.div>

          <motion.button 
            className="mobile-menu-toggle" 
            onClick={() => setIsOpen(!isOpen)}
            whileTap={{ scale: 0.9 }}
            aria-label={isOpen ? 'Fechar menu' : 'Abrir menu'}
            aria-expanded={isOpen}
          >
            <Menu size={24} />
          </motion.button>
        </div>
      </div>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div 
              className="mobile-menu-backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
            />
            <motion.div 
              className="mobile-menu-sidebar"
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            >
              <div className="mobile-sidebar-header">
                <div className="nav-brand">
                  <div className="nav-brand-icon">
                    <FileText size={20} color="white" weight="bold" />
                  </div>
                  <span className="nav-brand-text">LayrPDF</span>
                </div>
                <button className="sidebar-close" onClick={() => setIsOpen(false)}>
                  <X size={24} />
                </button>
              </div>

              <div className="mobile-menu-content">
                  <div className="mobile-menu-links">
                    <Link to="/" className="mobile-menu-link" onClick={() => { setIsOpen(false); scrollToHero(); }}>
                      <span>{t.nav_home}</span>
                      <ChevronRight size={18} />
                    </Link>
                    <a href="#como-funciona" className="mobile-menu-link" onClick={(e) => { setIsOpen(false); handleNavClick(e, '#como-funciona'); }}>
                      <span>{t.nav_how}</span>
                      <ChevronRight size={18} />
                    </a>
                    <a href="#por-que-gratis" className="mobile-menu-link" onClick={(e) => { setIsOpen(false); handleNavClick(e, '#por-que-gratis'); }}>
                      <span>{t.nav_why}</span>
                      <ChevronRight size={18} />
                    </a>
                    <Link to="/sobre" className="mobile-menu-link" onClick={() => setIsOpen(false)}>
                      <span>{t.nav_about}</span>
                      <ChevronRight size={18} />
                    </Link>
                    <Link to="/faq" className="mobile-menu-link" onClick={() => setIsOpen(false)}>
                      <span>{t.nav_faq}</span>
                      <ChevronRight size={18} />
                    </Link>
                  </div>
                  
                  <div className="mobile-menu-footer">
                    <div className="mobile-menu-actions">
                      <button 
                        className="theme-toggle-btn" 
                        onClick={() => setSiteLang(siteLang === 'pt' ? 'en' : 'pt')} 
                      >
                        {siteLang === 'pt' ? 'English (EN)' : 'Português (PT-BR)'}
                      </button>
                      
                      <button 
                        className="theme-toggle-btn" 
                        onClick={toggleTheme} 
                      >
                        {theme === 'dark' ? <><Sun size={18} /> {t.theme_light}</> : <><Moon size={18} /> {t.theme_dark}</>}
                      </button>
                    </div>

                  <button 
                    className="nav-cta mobile-cta" 
                    onClick={() => { setIsOpen(false); isHome ? scrollToApp() : navigate('/'); }}
                  >
                    {t.nav_cta}
                  </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </nav>
  );
}
