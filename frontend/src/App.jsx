import { useState, useEffect, useRef } from 'react'
import { X } from 'lucide-react'
import { TitleBar } from './components/layout/TitleBar'
import { motion, AnimatePresence } from 'framer-motion'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, useTheme } from './contexts/ThemeContext'
import { LanguageProvider, useLanguage } from './contexts/LanguageContext'
import Navbar from './components/layout/Navbar'
import About from './pages/About'
import FAQ from './pages/FAQ'

import { API_BASE } from './i18n/translations'
import { useTranslation } from './hooks/useTranslation'
import './styles/globals.css'
import './styles/Common.css'
import './App.css'

import { Hero } from './components/sections/Hero'
import { HowItWorks } from './components/sections/HowItWorks'
import { WhyFree } from './components/sections/WhyFree'
import { Downloads } from './components/sections/Downloads'
import { Footer } from './components/layout/Footer'

import { PreviewModeSelector } from './components/features/PreviewModeSelector'
import { AppInterface } from './components/features/AppInterface'


function AppContent() {
  const isDesktop = !!window.pywebview;
  const { theme } = useTheme();
  const { siteLang, t } = useLanguage();
  const [previewMode, setPreviewMode] = useState(null)
  const [showDownloadMenu, setShowDownloadMenu] = useState(false)
  const appRef = useRef(null)
  const heroRef = useRef(null)

  const translation = useTranslation(t);
  const { error, setError } = translation;

  const scrollToApp = () => {
    appRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const scrollToHero = () => {
    heroRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className={`page-wrapper ${isDesktop ? 'has-title-bar' : ''}`}>
      <TitleBar />
      {!isDesktop && <Navbar scrollToApp={scrollToApp} scrollToHero={scrollToHero} />}

      <Routes>
        <Route path="/" element={
          <main>
            {!isDesktop && (
              <>
                <Hero t={t} siteLang={siteLang} scrollToApp={scrollToApp} heroRef={heroRef} />

                <HowItWorks t={t} />

                <WhyFree t={t} />
              </>
            )}

            <AppInterface 
              t={t} 
              appRef={appRef} 
              translationProps={{
                ...translation,
                showDownloadMenu,
                setShowDownloadMenu,
                previewMode,
                setPreviewMode
              }} 
              API_BASE={API_BASE}
              theme={theme}
              isDesktop={isDesktop}
            />

            <Downloads t={t} scrollToApp={scrollToApp} />
            <Footer scrollToHero={scrollToHero} />
          </main>
        } />
        <Route path="/sobre" element={<main><About /></main>} />
        <Route path="/faq" element={<main><FAQ /></main>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {error && (
        <motion.div
          className="toast-error"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
        >
          <span>{error}</span>
          <button onClick={() => setError(null)} className="toast-close" aria-label="Fechar erro">
            <X size={18} />
          </button>
        </motion.div>
      )}

    </div>
  )
}

function App() {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </LanguageProvider>
    </ThemeProvider>
  )
}

export default App
