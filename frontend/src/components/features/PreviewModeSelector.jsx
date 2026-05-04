import { motion } from 'framer-motion';
import { Layout, Columns } from 'lucide-react';
import './PreviewModeSelector.css';

export const PreviewModeSelector = ({ onSelect, t }) => {
  return (
    <div className="preview-mode-selector">
      <motion.div 
        className="mode-card"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => onSelect('single')}
      >
        <div className="mode-icon"><Layout size={28} /></div>
        <h4>{t.mode_single_title}</h4>
        <p>{t.mode_single_desc}</p>
      </motion.div>
      <motion.div 
        className="mode-card"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => onSelect('side')}
      >
        <div className="mode-icon"><Columns size={28} /></div>
        <h4>{t.mode_side_title}</h4>
        <p>{t.mode_side_desc}</p>
      </motion.div>
    </div>
  );
};
