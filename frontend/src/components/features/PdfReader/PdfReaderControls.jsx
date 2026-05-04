import React from 'react';
import { ZoomOut, ZoomIn, RotateCcw } from 'lucide-react';

export const PdfReaderControls = ({
  zoom,
  setZoom,
  isSyncing,
  setIsSyncing
}) => {
  return (
    <div className="reader-footer-floating">
      <div className="zoom-controls">
        <button className="zoom-btn" onClick={() => setZoom(z => Math.max(50, z - 10))}>
          <ZoomOut size={18} />
        </button>
        <div className="zoom-level">{zoom}%</div>
        <button className="zoom-btn" onClick={() => setZoom(z => Math.min(250, z + 10))}>
          <ZoomIn size={18} />
        </button>
        <div className="zoom-divider" />
        <button 
          className={`sync-btn ${isSyncing ? 'active' : ''}`} 
          onClick={() => setIsSyncing(!isSyncing)}
          title="Sincronizar rolagem"
        >
          <RotateCcw size={16} />
        </button>
      </div>
    </div>
  );
};
