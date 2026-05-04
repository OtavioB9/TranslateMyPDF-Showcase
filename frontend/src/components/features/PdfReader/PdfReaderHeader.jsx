import React from 'react';
import { ChevronLeft, ChevronRight, Download, X } from 'lucide-react';

export const PdfReaderHeader = ({ 
  t, 
  currentPage, 
  pageCount, 
  setCurrentPage, 
  handleDownload, 
  onClose 
}) => {
  return (
    <header className="reader-header">
      <div className="reader-info">
        <div className="reader-logo">LayrPDF <span>Reader</span></div>
        <div className="reader-page-indicator">
          {t.preview_page} {currentPage + 1} / {pageCount}
        </div>
      </div>
      
      <div className="reader-controls">
        <div className="reader-nav-group">
          <button 
            className="reader-btn" 
            onClick={() => setCurrentPage(p => Math.max(0, p - 1))}
            disabled={currentPage === 0}
          >
            <ChevronLeft size={20} />
          </button>
          <button 
            className="reader-btn" 
            onClick={() => setCurrentPage(p => Math.min(pageCount - 1, p + 1))}
            disabled={currentPage === pageCount - 1}
          >
            <ChevronRight size={20} />
          </button>
        </div>

        <div className="reader-divider" />
        
        <button className="reader-btn secondary" onClick={handleDownload} title={t.download_btn}>
          <Download size={18} />
        </button>
        
        <button className="reader-btn close" onClick={onClose} title={t.close_btn}>
          <X size={20} />
        </button>
      </div>
    </header>
  );
};
