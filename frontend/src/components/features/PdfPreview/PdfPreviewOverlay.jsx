import React from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, Eye, EyeOff, Download, File, Layers, 
  ArrowRight, X, ChevronFirst, ChevronsLeft, 
  ChevronLeft, ChevronRight, ChevronsRight, ChevronLast 
} from 'lucide-react';
import { transitionVariants } from './variants';

export const PdfPreviewOverlay = ({
  isExpanded,
  setIsExpanded,
  t,
  currentPage,
  pageCount,
  mode,
  toggleVersion,
  showOriginal,
  showDownloadMenu,
  setShowDownloadMenu,
  handleDownload,
  pageRange,
  setPageRange,
  handleRangeDownload,
  setZoom,
  expandedDragX,
  handleDragEnd,
  leftScrollRef,
  rightScrollRef,
  syncScroll,
  handleMouseMove,
  zoom,
  mousePos,
  jobId,
  apiBase,
  paginate,
  direction,
  actionType
}) => {
  if (!isExpanded) return null;

  return createPortal(
    <div 
      className="expanded-overlay"
      onWheel={(e) => {
        const delta = e.deltaY * -0.001;
        setZoom(prev => Math.min(Math.max(1, prev + delta), 4));
      }}
    >
        <div className="expanded-header">
            <div className="expanded-header-left">
              <FileText size={18} color="#ef4444" />
              <span className="hide-mobile">{t.reading_mode} — </span>
              <span>{t.page} {currentPage + 1} {t.page_of} {pageCount}</span>
            </div>
            
            <div className="header-actions-group" style={{ position: 'relative' }}>
              {mode === 'single' && (
                <motion.button 
                  onClick={toggleVersion}
                  className="reader-btn"
                  whileHover={{ y: -4, scale: 1.02, color: '#ef4444' }}
                  whileTap={{ scale: 0.98 }}
                  data-label-mobile={showOriginal ? "Traduzido" : "Original"}
                >
                  {showOriginal ? <Eye size={18} /> : <EyeOff size={18} />}
                  <span className="btn-text">{showOriginal ? t.preview_view_translated : t.preview_view_original}</span>
                </motion.button>
              )}
              
              <motion.button 
                onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                className="reader-btn download"
                whileHover={{ y: -4, scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Download size={18} />
                <span className="btn-text">Download PDF</span>
              </motion.button>

              <AnimatePresence>
                {showDownloadMenu && (
                  <>
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      onClick={() => setShowDownloadMenu(false)}
                      style={{ position: 'fixed', inset: 0, zIndex: 100 }}
                    />
                    <motion.div 
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 10, scale: 0.95 }}
                      style={{
                        position: 'absolute',
                        top: 'calc(100% + 10px)',
                        right: 0,
                        width: '320px',
                        background: 'var(--dropdown-bg)',
                        backdropFilter: 'blur(20px)',
                        borderRadius: '20px',
                        border: 'var(--glass-border)',
                        boxShadow: 'var(--dropdown-shadow)',
                        padding: '1.25rem',
                        zIndex: 99999,
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '1rem'
                      }}
                    >
                      <motion.div 
                        onClick={handleDownload}
                        className="download-option"
                        whileHover={{ 
                          y: -5, 
                          backgroundColor: 'rgba(255,255,255,0.08)',
                          boxShadow: '0 20px 40px rgba(0,0,0,0.4), 0 0 20px rgba(239, 68, 68, 0.15)',
                        }}
                        whileTap={{ scale: 0.98 }}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '1rem',
                          padding: '1.5rem',
                          borderRadius: '14px',
                          cursor: 'pointer',
                          background: 'var(--bg-card)',
                          border: '1px solid transparent',
                          transition: 'all 0.2s ease'
                        }}
                      >
                        <div style={{
                          width: '40px', height: '40px', borderRadius: '10px',
                          background: 'var(--accent-rose-soft)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          color: 'var(--accent-rose)'
                        }}>
                          <File size={20} />
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-heading)' }}>{t.dl_full_pdf}</span>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t.dl_full_pdf_desc}</span>
                        </div>
                      </motion.div>

                      <div style={{ height: '1px', background: 'var(--border)', margin: '0 0.5rem' }} />

                      <motion.div 
                        whileHover={{ 
                          y: -5, 
                          backgroundColor: 'rgba(255,255,255,0.08)',
                          boxShadow: '0 20px 40px rgba(0,0,0,0.4), 0 0 20px rgba(239, 68, 68, 0.15)',
                        }}
                        style={{ 
                          display: 'flex', 
                          flexDirection: 'column', 
                          gap: '0.75rem', 
                          padding: '1.25rem',
                          borderRadius: '14px',
                          background: 'var(--bg-card)',
                          border: '1px solid transparent',
                          transition: 'all 0.2s ease'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                          <div style={{ color: 'var(--accent-rose)' }}>
                            <Layers size={20} />
                          </div>
                          <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-heading)' }}>{t.dl_selected_pages}</span>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t.dl_total}: {pageCount} {t.dl_pages_suffix}</span>
                          </div>
                        </div>

                        <form onSubmit={handleRangeDownload} style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem' }}>
                          <input 
                            type="text"
                            placeholder="Ex: 1-5, 8, 12"
                            value={pageRange}
                            onChange={(e) => setPageRange(e.target.value)}
                            autoFocus
                            style={{
                              flex: 1,
                              background: 'var(--bg-card)',
                              border: 'var(--glass-border)',
                              borderRadius: '12px',
                              padding: '0.75rem 1rem',
                              color: 'var(--text-heading)',
                              fontSize: '0.85rem',
                              outline: 'none'
                            }}
                          />
                          <motion.button
                            whileHover={{ scale: 1.05, backgroundColor: '#ef4444' }}
                            whileTap={{ scale: 0.95 }}
                            type="submit"
                            style={{
                              width: '42px', height: '42px', borderRadius: '10px',
                              background: 'var(--accent-rose)', border: 'none',
                              color: 'white', cursor: 'pointer', display: 'flex',
                              alignItems: 'center', justifyContent: 'center'
                            }}
                          >
                            <ArrowRight size={18} />
                          </motion.button>
                        </form>
                      </motion.div>
                    </motion.div>
                  </>
                )}
              </AnimatePresence>

              <motion.button 
                onClick={() => {
                  setIsExpanded(false);
                  setZoom(1);
                }}
                className="expanded-close-btn"
                whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
                whileTap={{ scale: 0.9 }}
              >
                <X size={20} />
              </motion.button>
            </div>
          </div>

          <div className="expanded-content">
            <motion.div 
              className="expanded-panels"
              onDoubleClick={() => mode === 'single' && toggleVersion()}
              drag="x"
              dragConstraints={{ left: 0, right: 0 }}
              dragElastic={0.7}
              dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
              style={{ x: expandedDragX }}
              onDragEnd={handleDragEnd}
              whileDrag={{ cursor: 'grabbing' }}
            >
              {(mode === 'side' || showOriginal) && (
                <div className="expanded-panel">
                  <span className="panel-label">{t.label_original}</span>
                  <div 
                    className="panel-image-container" 
                    ref={leftScrollRef} 
                    onScroll={syncScroll}
                    onMouseMove={handleMouseMove}
                  >
                    <AnimatePresence mode="wait" custom={{ direction, actionType }}>
                      <motion.img 
                        key={`original-${currentPage}`}
                        src={`${apiBase}/preview/${jobId}/${currentPage}?version=original`} 
                        className="expanded-image"
                        alt="Original"
                        custom={{ direction, actionType }}
                        variants={transitionVariants}
                        initial="enter"
                        animate={{ 
                          ...transitionVariants.center, 
                          scale: zoom,
                          originX: mousePos.x,
                          originY: mousePos.y
                        }}
                        exit="exit"
                        style={{ 
                          cursor: zoom > 1 ? 'zoom-out' : 'zoom-in',
                          zIndex: 1
                        }}
                      />
                    </AnimatePresence>
                  </div>
                </div>
              )}

              {(mode === 'side' || !showOriginal) && (
                <div className="expanded-panel">
                  <span className="panel-label">{t.label_translated}</span>
                  <div 
                    className="panel-image-container" 
                    ref={rightScrollRef} 
                    onScroll={syncScroll}
                    onMouseMove={handleMouseMove}
                  >
                    <AnimatePresence mode="wait" custom={{ direction, actionType }}>
                      <motion.img 
                        key={`translated-${currentPage}`}
                        src={`${apiBase}/preview/${jobId}/${currentPage}?version=translated`} 
                        className="expanded-image"
                        alt="Translated"
                        custom={{ direction, actionType }}
                        variants={transitionVariants}
                        initial="enter"
                        animate={{ 
                          ...transitionVariants.center, 
                          scale: zoom,
                          originX: mousePos.x,
                          originY: mousePos.y
                        }}
                        exit="exit"
                        style={{ 
                          cursor: zoom > 1 ? 'zoom-out' : 'zoom-in',
                          zIndex: 1
                        }}
                      />
                    </AnimatePresence>
                  </div>
                </div>
              )}
            </motion.div>
          </div>

          <div className="expanded-pagination">
              <motion.button 
                onClick={() => paginate(0 - currentPage)} 
                disabled={currentPage === 0}
                className="preview-nav-btn"
                title="Primeira Página"
                whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
                whileTap={{ scale: 0.9 }}
              >
                <ChevronFirst size={18} />
              </motion.button>

              <motion.button 
                onClick={() => paginate(Math.max(0, currentPage - 10) - currentPage)} 
                disabled={currentPage === 0}
                className="preview-nav-btn"
                title="-10 Páginas"
                whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
                whileTap={{ scale: 0.9 }}
              >
                <ChevronsLeft size={18} />
              </motion.button>

              <motion.button 
                onClick={() => paginate(-1)} 
                disabled={currentPage === 0}
                className="preview-nav-btn"
                whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
                whileTap={{ scale: 0.9 }}
              >
                <ChevronLeft size={20} />
              </motion.button>

              <div className="preview-page-info">
                <span style={{ color: '#ef4444' }}>{currentPage + 1}</span>
                <span> / </span>
                <span>{pageCount}</span>
              </div>

              <motion.button 
                onClick={() => paginate(1)} 
                disabled={currentPage === pageCount - 1}
                className="preview-nav-btn"
                whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
                whileTap={{ scale: 0.9 }}
              >
                <ChevronRight size={20} />
              </motion.button>

              <motion.button 
                onClick={() => paginate(Math.min(pageCount - 1, currentPage + 10) - currentPage)} 
                disabled={currentPage === pageCount - 1}
                className="preview-nav-btn"
                title="+10 Páginas"
                whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
                whileTap={{ scale: 0.9 }}
              >
                <ChevronsRight size={18} />
              </motion.button>

              <motion.button 
                onClick={() => paginate((pageCount - 1) - currentPage)} 
                disabled={currentPage === pageCount - 1}
                className="preview-nav-btn"
                title="Última Página"
                whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
                whileTap={{ scale: 0.9 }}
              >
                <ChevronLast size={18} />
              </motion.button>
          </div>
      </div>,
    document.body
  );
};
