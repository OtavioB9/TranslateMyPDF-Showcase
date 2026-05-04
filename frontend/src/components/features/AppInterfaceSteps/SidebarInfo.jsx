import { Activity, FileText, Settings } from 'lucide-react';
import './SidebarInfo.css';

export const SidebarInfo = ({
  t,
  status,
  fileList,
  currentFileIndex,
  fileTotalPages,
  limitPages,
  sourceLang,
  targetLang
}) => {
  return (
    <div className="info-sidebar">
      <div className="sidebar-section">
        <span className="sidebar-label"><Activity size={14} /> {t.sidebar_stats}</span>
        <div className="stat-row">
          <span>{t.sidebar_pages_to_translate}</span>
          <strong>{status?.translate_limit || limitPages || status?.total_pages || '?'}</strong>
        </div>
        <div className="stat-row">
          <span>{t.sidebar_total_pages}</span>
          <strong>{fileTotalPages || status?.total_pages || '?'}</strong>
        </div>
        <div className="dropdown-divider-v2" />
        <div className="stat-row filename-row">
          <span className="sidebar-file-label">{t.sidebar_file}</span>
          <div className="sidebar-file-content">
            <FileText size={14} className="icon-red" />
            <strong>
              {status?.filename || (currentFileIndex !== null ? fileList[currentFileIndex]?.file.name : 'PDF')}
            </strong>
          </div>
        </div>
      </div>
      
      <div className="sidebar-section">
        <span className="sidebar-label"><Settings size={14} /> {t.sidebar_config}</span>
        <div className="mini-info">
          <div className="info-item">
             <span>{t.sidebar_source}</span>
            <strong>{sourceLang === 'en' ? t.opt_en : t.opt_pt}</strong>
          </div>
          <div className="info-item">
             <span>{t.sidebar_target}</span>
            <strong>{targetLang === 'pt' ? t.opt_pt : t.opt_en}</strong>
          </div>
        </div>
      </div>
    </div>
  );
};
