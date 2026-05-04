import './TitleBar.css';
import { Monitor, X, FileText } from 'lucide-react';

export const TitleBar = () => {
  if (!window.pywebview) return null;

  return (
    <div className="title-bar">
      <div className="title-bar-drag-region">
        <div className="title-bar-title">
          <FileText size={14} className="icon-red" />
          <span>LayrPDF</span>
        </div>
      </div>
      <div className="title-bar-controls">
        <button className="control-btn minimize" onClick={() => window.pywebview.api.minimize()}>
          <Monitor size={14} />
        </button>
        <button className="control-btn close" onClick={() => window.pywebview.api.close()}>
          <X size={14} />
        </button>
      </div>
    </div>
  );
};
