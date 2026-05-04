import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, ChevronLeft, Download, FileText, Layers, ArrowRight } from 'lucide-react';
import { PdfPreview } from '../PdfPreview/index';
import { PreviewModeSelector } from '../PreviewModeSelector';
import './ResultStep.css';

export const ResultStep = ({
  t,
  status,
  previewMode,
  setPreviewMode,
  jobId,
  apiBase,
  limitPages,
  fileTotalPages,
  showDownloadMenu,
  setShowDownloadMenu,
  handleDownloadAction,
  pageRange,
  handlePageRangeChange,
  resetAll
}) => {

  return (
    <motion.div 
      key="completed" 
      initial={{ opacity: 0, scale: 0.98 }} 
      animate={{ opacity: 1, scale: 1 }} 
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ duration: 0.4 }}
      className="result-section-v2"
    >
      <div className="results-header">
        <div className="icon-red-success">
          <CheckCircle size={44} />
          <div className="success-glow"></div>
        </div>
        <h2 className="results-title">{t.res_title}</h2>
        <p className="results-desc">{t.res_desc}</p>
      </div>

      <AnimatePresence mode="wait">
        {previewMode === null ? (
          <motion.div 
            key="selector"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <PreviewModeSelector onSelect={setPreviewMode} t={t} />
          </motion.div>
        ) : (
          <motion.div 
            key="active-preview"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.3 }}
            className="preview-active-zone"
          >
            <PdfPreview 
              jobId={jobId} 
              apiBase={apiBase} 
              t={t} 
              status={status?.status} 
              limitPages={limitPages} 
              mode={previewMode}
            />
            <button className="btn-back-preview" onClick={() => setPreviewMode(null)}>
              <ChevronLeft size={18} /> <span>{t.btn_back}</span>
            </button>
          </motion.div>
        )}
      </AnimatePresence>
      
      <div className="success-actions">
        <div className="download-wrapper-v2">
          <button 
            className="btn-rose-v2" 
            onClick={() => setShowDownloadMenu(!showDownloadMenu)}
          >
            <Download size={20} /> <span>{t.res_dl}</span>
          </button>
          
          <AnimatePresence>
            {showDownloadMenu && (
              <motion.div 
                className="download-dropdown-v2"
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                transition={{ type: 'spring', stiffness: 200, damping: 20 }}
              >
                <motion.div 
                  className="dropdown-item-v2" 
                  onClick={() => handleDownloadAction('full')}
                  whileHover={{ 
                    y: -4, 
                    backgroundColor: 'rgba(255,255,255,0.08)',
                    boxShadow: '0 20px 40px rgba(0,0,0,0.4), 0 0 20px rgba(239, 68, 68, 0.15)',
                  }}
                  whileTap={{ scale: 0.98 }}
                >
                  <FileText size={16} className="icon-red" />
                  <div className="item-text">
                    <strong>{t.dl_full_pdf}</strong>
                    <span>{t.dl_full_pdf_desc}</span>
                  </div>
                </motion.div>
                
                <div className="dropdown-divider-v2" />
                
                <motion.div 
                  className="dropdown-item-v2 custom-range"
                  whileHover={{ 
                    y: -4, 
                    backgroundColor: 'rgba(255,255,255,0.06)',
                    boxShadow: '0 20px 40px rgba(0,0,0,0.4), 0 0 20px rgba(239, 68, 68, 0.15)',
                  }}
                >
                  <div className="item-header">
                    <Layers size={16} className="icon-red" />
                    <div className="item-text">
                      <strong>{t.dl_selected_pages}</strong>
                      <span>{t.dl_total}: {status?.translate_limit || limitPages || fileTotalPages} {t.dl_pages_suffix}</span>
                    </div>
                  </div>
                  <form className="range-input-row" onSubmit={(e) => { e.preventDefault(); handleDownloadAction('range'); }}>
                    <input 
                      type="text" 
                      placeholder="Ex: 1-5, 8, 12" 
                      value={pageRange}
                      onChange={handlePageRangeChange}
                      onClick={(e) => e.stopPropagation()}
                    />
                    <motion.button 
                      className="btn-mini-send"
                      disabled={!pageRange}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={(e) => {
                        e.stopPropagation();
                      }}
                      type="submit"
                    >
                      <ArrowRight size={16} />
                    </motion.button>
                  </form>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <button className="btn-ghost-v2" onClick={resetAll}>
          <span>{t.res_another}</span>
        </button>
      </div>
    </motion.div>
  );
};
