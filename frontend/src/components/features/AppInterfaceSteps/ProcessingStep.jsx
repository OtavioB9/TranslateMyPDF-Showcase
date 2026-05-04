import { motion } from 'framer-motion';
import { AlertCircle, FileText, Loader2 } from 'lucide-react';
import { FluidCounter } from '../../common/FluidCounter';
import { LoadingDots } from '../../common/LoadingDots';
import { Skeleton } from '../../common/Skeleton';
import './ProcessingStep.css';

export const ProcessingStep = ({
  t,
  status,
  fileList,
  currentFileIndex,
  fileTotalPages,
  displayProgress,
  displayWidth,
  stableEta,
  resetAll
}) => {
  return (
    <motion.div 
      key="processing" 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      exit={{ opacity: 0, y: -20 }} 
      transition={{ type: 'spring', stiffness: 100, damping: 20 }} 
      className="processing-zone"
    >
      {status?.status === 'failed' ? (
        <div className="error-zone">
          <AlertCircle size={48} className="icon-red" />
          <h3>{t.err_title}</h3>
          <p>{status?.error || t.err_unexp}</p>
          <button className="btn-rose-v2" onClick={resetAll} style={{ marginTop: '1rem' }}>{t.btn_retry}</button>
        </div>
      ) : (
        <div className="processing-details">
          <div className="proc-file-row">
            <div className="proc-file-info">
              <div className="proc-file-icon"><FileText size={22} className="icon-red" /></div>
              <div>
                <div className="proc-file-name">
                  {status?.filename || (currentFileIndex !== null ? fileList[currentFileIndex]?.file?.name : (fileList.length > 0 ? fileList[0]?.file?.name : 'PDF'))}
                </div>
                <div className="proc-file-pages">
                  <FluidCounter value={status?.current_page || 0} /> de {status?.translate_limit || status?.total_pages || fileTotalPages || '?'} {t.up_total}
                </div>
              </div>
            </div>
            <span className="proc-badge processing">{t.proc_badge}</span>
          </div>

          <div className="proc-progress">
            <div className="proc-progress-header">
              <span className="proc-chapter">
                {(() => {
                  const raw = status?.current_chapter || t.proc_analyzing
                  const base = raw.replace(/\.+$/, '')
                  if (/\.{1,3}$/.test(raw) || raw === t.proc_analyzing) {
                    return <>{base}<LoadingDots /></>
                  }
                  return raw
                })()}
              </span>
              <motion.span className="proc-percent">{displayProgress}</motion.span>
            </div>
            <div className="proc-bar-bg">
              <motion.div
                className="proc-bar-fill"
                style={{ width: displayWidth }}
              />
            </div>
            {(status?.eta > 0 || status === null) && (
              <motion.div
                className="proc-eta"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Loader2 size={16} className="icon-spin" />
                {status === null ? (
                  <span>{t.proc_starting}<LoadingDots /></span>
                ) : (
                  <span>{t.proc_time} <strong>{stableEta || Math.round(status.eta) || '...'}s</strong></span>
                )}
              </motion.div>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
};
