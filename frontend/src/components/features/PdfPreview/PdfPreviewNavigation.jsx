import React from 'react';
import { motion } from 'framer-motion';
import { 
  ChevronLeft, 
  ChevronRight, 
  ChevronsLeft, 
  ChevronsRight, 
  ChevronFirst, 
  ChevronLast 
} from 'lucide-react';

export const PdfPreviewNavigation = ({ 
  pageCount, 
  currentPage, 
  paginate, 
  isPreloading 
}) => {
  if (pageCount <= 1) return null;

  return (
    <div className="preview-nav" style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      gap: '1rem', 
      padding: '1.25rem 0',
      alignItems: 'center'
    }}>
      <div style={{ display: 'flex', gap: '0.8rem', alignItems: 'center' }}>
        <motion.button
          onClick={() => {
            const target = 0 - currentPage;
            paginate(target);
          }}
          disabled={currentPage === 0 || isPreloading}
          className="preview-nav-btn"
          title="Primeira Página"
          whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
          whileTap={{ scale: 0.9 }}
          transition={{ type: 'spring', stiffness: 400, damping: 17 }}
        >
          <ChevronFirst size={18} />
        </motion.button>

        <motion.button
          onClick={() => {
            const target = Math.max(0, currentPage - 10) - currentPage;
            paginate(target);
          }}
          disabled={currentPage === 0 || isPreloading}
          className="preview-nav-btn hide-mobile"
          title="-10 Páginas"
          whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
          whileTap={{ scale: 0.9 }}
          transition={{ type: 'spring', stiffness: 400, damping: 17 }}
        >
          <ChevronsLeft size={18} />
        </motion.button>

        <motion.button
          onClick={() => paginate(-1)}
          disabled={currentPage === 0 || isPreloading}
          className="preview-nav-btn"
          title="Anterior"
          whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
          whileTap={{ scale: 0.9 }}
          transition={{ type: 'spring', stiffness: 400, damping: 17 }}
        >
          <ChevronLeft size={20} />
        </motion.button>
        
        <div className="preview-page-info">
          <span>{currentPage + 1}</span>
          <span className="sep">/</span>
          <span>{pageCount}</span>
        </div>

        <motion.button
          onClick={() => paginate(1)}
          disabled={currentPage >= pageCount - 1 || isPreloading}
          className="preview-nav-btn"
          title="Próxima"
          whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
          whileTap={{ scale: 0.9 }}
          transition={{ type: 'spring', stiffness: 400, damping: 17 }}
        >
          <ChevronRight size={20} />
        </motion.button>

        <motion.button
          onClick={() => {
            const target = Math.min(pageCount - 1, currentPage + 10) - currentPage;
            paginate(target);
          }}
          disabled={currentPage >= pageCount - 1 || isPreloading}
          className="preview-nav-btn hide-mobile"
          title="+10 Páginas"
          whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
          whileTap={{ scale: 0.9 }}
          transition={{ type: 'spring', stiffness: 400, damping: 17 }}
        >
          <ChevronsRight size={18} />
        </motion.button>

        <motion.button
          onClick={() => {
            const target = (pageCount - 1) - currentPage;
            paginate(target);
          }}
          disabled={currentPage >= pageCount - 1 || isPreloading}
          className="preview-nav-btn"
          title="Última Página"
          whileHover={{ y: -4, scale: 1.1, color: '#ef4444' }}
          whileTap={{ scale: 0.9 }}
          transition={{ type: 'spring', stiffness: 400, damping: 17 }}
        >
          <ChevronLast size={18} />
        </motion.button>
      </div>
    </div>
  );
};
