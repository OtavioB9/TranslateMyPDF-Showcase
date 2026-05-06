import { useState, useEffect } from 'react';
import { CheckCircle, ArrowRight } from 'lucide-react';
import HeroAnimation from './HeroAnimation';
import './Hero.css';

export const Hero = ({ t, siteLang, scrollToApp, heroRef }) => {
  const [shouldRenderVisual, setShouldRenderVisual] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShouldRenderVisual(true), 150);
    return () => clearTimeout(timer);
  }, []);

  return (
    <section className="hero" ref={heroRef}>
      <div className="container">
        <div className="hero-grid">
          <div>
            <div className="animate-fade-up delay-1">
              <span className="hero-badge">
                <CheckCircle size={14} /> {t.hero_badge}
              </span>
            </div>

            <h1 className="animate-fade-up delay-2">
              LayrPDF
            </h1>

            <p className="hero-subtitle animate-fade-up delay-3">
              {t.hero_sub_1}<br />
              {t.hero_sub_2}<br />
              {t.hero_sub_3}
            </p>

            <div className="hero-actions animate-fade-up delay-4">
              <button 
                className="btn-dark" 
                onClick={scrollToApp}
              >
                {t.hero_btn_start} <ArrowRight size={18} />
              </button>
              <a 
                href="#como-funciona" 
                className="btn-ghost"
              >
                {t.hero_btn_more}
              </a>
            </div>
          </div>

          <div className="hero-visual animate-fade-up delay-4">
            {shouldRenderVisual && <HeroAnimation siteLang={siteLang} />}
          </div>
        </div>
      </div>
    </section>
  );
};
