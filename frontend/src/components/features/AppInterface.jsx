import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadStep } from './AppInterfaceSteps/UploadStep';
import { ReadyStep } from './AppInterfaceSteps/ReadyStep';
import { ResultStep } from './AppInterfaceSteps/ResultStep';
import { ProcessingStep } from './AppInterfaceSteps/ProcessingStep';
import { SidebarInfo } from './AppInterfaceSteps/SidebarInfo';
import { useSound } from '../../hooks/useSound';

import './AppInterface.css';

export const AppInterface = ({ 
  t, 
  appRef, 
  translationProps,
  API_BASE,
  theme,
  isDesktop
}) => {
  const {
    fileList,
    currentFileIndex,
    jobId,
    status,
    isUploading,
    limitPages,
    sourceLang,
    targetLang,
    isCounting,
    fileTotalPages,
    hasStartedTranslation,
    pageRange,
    engineOnline,
    handleUpload: originalHandleUpload,
    handleTranslate: originalHandleTranslate,
    resetAll: originalResetAll,
    handleLimitChange,
    handleKeyDown,
    handlePageRangeChange,
    setSourceLang,
    setTargetLang,
    setError,
    showDownloadMenu,
    setShowDownloadMenu,
    previewMode,
    setPreviewMode,
    stableEta,
    displayProgress,
    displayWidth
  } = translationProps;

  const { playSound, loadSound, initContext } = useSound();

  useEffect(() => {
    loadSound('click', '/sounds/click.mp3');
    loadSound('success', '/sounds/success.mp3');
    loadSound('upload', '/sounds/upload.mp3');
  }, [loadSound]);

  const handleUpload = (e) => {
    initContext();
    playSound('upload', 0.3);
    originalHandleUpload(e);
  };

  const handleTranslate = async () => {
    playSound('click', 0.4);
    await originalHandleTranslate();
  };

  const resetAll = () => {
    playSound('click', 0.2);
    originalResetAll();
  };

  useEffect(() => {
    if (status?.status === 'completed') {
      playSound('success', 0.4);
    }
  }, [status?.status, playSound]);

  const handleDownloadAction = async (type) => {
    let url = '';
    
    const originalName = status?.filename || 
                         (currentFileIndex !== null ? fileList[currentFileIndex]?.file?.name : 'document.pdf');
    
    const baseName = originalName.replace(/\.[^/.]+$/, "");
    let filename = `${baseName} (traduzido).pdf`;
    
    if (type === 'full') {
      url = `${API_BASE}/download/${jobId}`;
    } else {
      url = `${API_BASE}/download/${jobId}/pages?pages=${pageRange.replace(/\s/g, '')}`;
      filename = `${baseName}_Paginas_Selecionadas (traduzido).pdf`;
    }

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      
      setTimeout(() => {
        document.body.removeChild(link);
        window.URL.revokeObjectURL(blobUrl);
      }, 100);
      
      setShowDownloadMenu(false);
    } catch (err) {
      console.error('Download error:', err);
      window.open(url, '_blank');
      setShowDownloadMenu(false);
    }
  };

  return (
    <section className="app-section" id="traduzir" ref={appRef}>
      <div className="container">
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="app-header"
        >
          <p className="section-label">{t.app_label}</p>
          <h2 className="section-title">
            {t.app_title}
          </h2>
        </motion.div>

        <motion.div 
          className="app-main-container"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className={`unified-card liquid-glass ${status?.status === 'completed' ? 'results-mode' : ''}`}>
            <div className="card-top-bar">
              <div className="card-tab active">{t.app_label}</div>
              {hasStartedTranslation && <div className="card-status-tag">{status?.status === 'completed' ? t.res_title : t.proc_badge}</div>}
            </div>

            <div className="card-content-wrapper">
              <div className={`main-zone ${(!hasStartedTranslation || status?.status === 'completed') ? 'full-width' : ''}`}>
                <AnimatePresence mode="wait">
                  <motion.div
                    key={fileList.length === 0 ? 'upload' : !hasStartedTranslation ? 'ready' : (status?.status === 'completed') ? 'result' : 'processing'}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ 
                      type: "spring",
                      stiffness: 80,
                      damping: 20,
                      mass: 1
                    }}
                    className="step-container"
                  >
                    {fileList.length === 0 ? (
                      <UploadStep t={t} handleUpload={handleUpload} />
                    ) : !hasStartedTranslation ? (
                      <ReadyStep 
                        t={t}
                        fileList={fileList}
                        sourceLang={sourceLang}
                        targetLang={targetLang}
                        setSourceLang={setSourceLang}
                        setTargetLang={setTargetLang}
                        isUploading={isUploading}
                        isCounting={isCounting}
                        fileTotalPages={fileTotalPages}
                        limitPages={limitPages}
                        handleLimitChange={handleLimitChange}
                        handleKeyDown={handleKeyDown}
                        resetAll={resetAll}
                        handleTranslate={handleTranslate}
                        jobId={jobId}
                        engineOnline={engineOnline}
                      />
                    ) : (status?.status === 'completed') ? (
                      <ResultStep
                        t={t}
                        status={status}
                        previewMode={previewMode}
                        setPreviewMode={setPreviewMode}
                        jobId={jobId}
                        apiBase={API_BASE}
                        limitPages={limitPages}
                        fileTotalPages={fileTotalPages}
                        showDownloadMenu={showDownloadMenu}
                        setShowDownloadMenu={setShowDownloadMenu}
                        handleDownloadAction={handleDownloadAction}
                        pageRange={pageRange}
                        handlePageRangeChange={handlePageRangeChange}
                        resetAll={resetAll}
                      />
                    ) : (
                      <ProcessingStep
                        t={t}
                        status={status}
                        fileList={fileList}
                        currentFileIndex={currentFileIndex}
                        fileTotalPages={fileTotalPages}
                        displayProgress={displayProgress}
                        displayWidth={displayWidth}
                        stableEta={stableEta}
                        resetAll={resetAll}
                      />
                    )}
                  </motion.div>
                </AnimatePresence>
              </div>

              {hasStartedTranslation && status?.status !== 'completed' && (
                <SidebarInfo
                  t={t}
                  status={status}
                  fileList={fileList}
                  currentFileIndex={currentFileIndex}
                  fileTotalPages={fileTotalPages}
                  limitPages={limitPages}
                  sourceLang={sourceLang}
                  targetLang={targetLang}
                />
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
