import React from 'react';
import { motion } from 'framer-motion';
import { Eye, EyeOff, Maximize2 } from 'lucide-react';

export const PdfPreviewHeader = ({ 
  isSide, 
  t, 
  showOriginal, 
  toggleVersion, 
  isPreloading, 
  setIsExpanded, 
  setZoom 
}) => {
  return (
    <div className="preview-header">
      <h3 className="preview-title">
        {isSide ? t.sidebar_pages : (showOriginal ? t.preview_original : t.preview_translated)}
      </h3>
      
      <div className="preview-header-right">
        {!isSide && (
          <button
            className="preview-toggle-btn"
            onClick={toggleVersion}
            disabled={isPreloading}
            style={{ opacity: isPreloading ? 0.6 : 1 }}
          >
            {showOriginal ? <Eye size={15} /> : <EyeOff size={15} />}
            {showOriginal ? t.preview_view_translated : t.preview_view_original}
          </button>
        )}

        <motion.button
          onClick={() => {
            setIsExpanded(true);
            setZoom(1);
          }}
          className="expand-preview-btn"
          whileHover={{ 
            scale: 1.25, 
            color: '#ef4444'
          }}
          whileTap={{ scale: 0.9 }}
          title="Modo Leitura (Clique duplo no PDF também funciona)"
        >
          <Maximize2 size={18} />
        </motion.button>
      </div>
    </div>
  );
};
