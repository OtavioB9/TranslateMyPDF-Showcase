import { motion } from 'framer-motion';
import { Upload } from 'lucide-react';
import './UploadStep.css';

export const UploadStep = ({ t, handleUpload }) => {
  return (
    <motion.div 
      key="idle" 
      className="upload-zone-v2"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ type: 'spring', stiffness: 80, damping: 20 }}
      onClick={() => document.getElementById('file-input-v2').click()}
    >
      <div className="pulse-circle">
        <Upload size={38} className="icon-red" />
      </div>
      <h3>{t.up_drag}</h3>
      <p>{t.up_no_limit}</p>
      <input 
        type="file" 
        id="file-input-v2" 
        hidden 
        onChange={handleUpload} 
        accept=".pdf"
        multiple
      />
    </motion.div>
  );
};
