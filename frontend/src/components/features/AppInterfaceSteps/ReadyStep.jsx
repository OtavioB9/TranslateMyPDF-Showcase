import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ChevronUp, ChevronDown } from 'lucide-react';
import { FluidCounter } from '../../common/FluidCounter';
import { LoadingDots } from '../../common/LoadingDots';
import { Skeleton } from '../../common/Skeleton';
import CustomSelect from '../../common/CustomSelect';
import './ReadyStep.css';
import { fadeUp } from '../../../styles/animations';

export const ReadyStep = ({ 
  t, 
  fileList, 
  sourceLang, 
  targetLang, 
  setSourceLang, 
  setTargetLang, 
  isUploading, 
  isCounting, 
  fileTotalPages, 
  limitPages, 
  handleLimitChange, 
  handleKeyDown, 
  resetAll, 
  handleTranslate, 
  jobId, 
  engineOnline 
}) => {
  const holdTimeout = useRef(null);
  const holdInterval = useRef(null);

  const cleanupTimers = () => {
    if (holdTimeout.current) clearTimeout(holdTimeout.current);
    if (holdInterval.current) clearInterval(holdInterval.current);
  };

  useEffect(() => {
    return cleanupTimers;
  }, []);

  const adjustPages = (amount) => {
    const currentVal = Number(limitPages || fileTotalPages || 0);
    const newVal = amount > 0 
      ? Math.min(currentVal + amount, fileTotalPages || 9999)
      : Math.max(currentVal + amount, 1);
    
    handleLimitChange({ target: { value: String(newVal) } });
  };

  const startHolding = (amount) => {
    adjustPages(amount);
    holdTimeout.current = setTimeout(() => {
      holdInterval.current = setInterval(() => adjustPages(amount), 50);
    }, 400);
  };

  return (
    <motion.div
      key="selected"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ type: 'spring', stiffness: 80, damping: 20 }}
      variants={{
        visible: { transition: { staggerChildren: 0.1 } }
      }}
      className="ready-zone"
    >
      <h2 className="card-shine-title">LAYRPDF</h2>

      <p className="file-count-label">{fileList.length} {t.file_count}</p>

      <div className="config-pills-stack">
        <motion.div 
          className="config-pill-card" 
          variants={fadeUp}
        >
          <div className="lang-pair-row">
            <div className="lang-pair-side">
              <span className="lang-pair-label">{t.config_from}</span>
              <CustomSelect
                value={sourceLang}
                options={[{value: 'en', label: t.opt_en}, {value: 'pt', label: t.opt_pt}]}
                onChange={setSourceLang}
                disabled={true}
              />
            </div>
            <div className="lang-pair-arrow">
              <ArrowRight size={20} strokeWidth={1.5} />
            </div>
            <div className="lang-pair-side">
              <span className="lang-pair-label">{t.config_to}</span>
              <CustomSelect
                value={targetLang}
                options={[{value: 'pt', label: t.opt_pt}, {value: 'en', label: t.opt_en}].filter(o => o.value !== sourceLang)}
                onChange={setTargetLang}
              />
            </div>
          </div>
        </motion.div>

        <motion.div className="pages-summary-card" variants={fadeUp}>
          <span className="summary-label">
            {isUploading ? (
              <>{t.up_reading}<LoadingDots /></>
            ) : (isCounting || !fileTotalPages ? (
              <>{t.up_counting}<LoadingDots /></>
            ) : (
              t.config_pages
            ))}
          </span>
          <div className="summary-count">
            <FluidCounter value={isCounting ? 0 : (limitPages || fileTotalPages || 0)} />
          </div>
          <div className="pages-input-wrapper">
            <input
              type="number"
              className="pages-pill-input-v2"
              value={isCounting ? '' : (limitPages || '')}
              onChange={handleLimitChange}
              onKeyDown={handleKeyDown}
              min="1"
              max={fileTotalPages || 9999}
              placeholder={isCounting ? '...' : t.opt_all}
              disabled={isUploading || isCounting}
            />
            <div className="pages-pill-controls">
              <button 
                className="pill-control-btn"
                onMouseDown={() => startHolding(1)}
                onMouseUp={cleanupTimers}
                onMouseLeave={cleanupTimers}
                disabled={isUploading || isCounting}
              >
                <ChevronUp size={14} />
              </button>
              <button 
                className="pill-control-btn"
                onMouseDown={() => startHolding(-1)}
                onMouseUp={cleanupTimers}
                onMouseLeave={cleanupTimers}
                disabled={isUploading || isCounting}
              >
                <ChevronDown size={14} />
              </button>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="action-row-v2">
        <button className="btn-ghost-v2 premium-btn-hover" onClick={resetAll}>{t.btn_back}</button>
        <button 
          className="btn-rose-v2" 
          onClick={handleTranslate} 
          disabled={isUploading || isCounting || !jobId}
        >
          <span>{t.btn_translate}</span>
        </button>
      </div>

      <div className={`engine-indicator ${engineOnline ? 'online' : 'offline'}`}>
        <span className="engine-dot"></span>
        <span>{engineOnline ? t.engine_online : t.engine_offline}</span>
      </div>
    </motion.div>
  );
};
