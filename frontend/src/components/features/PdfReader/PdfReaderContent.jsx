import React from 'react';

export const PdfReaderContent = ({
  t,
  displaySrc,
  isPreloading,
  zoom,
  scrollRefOrig,
  scrollRefTrans,
  handleSyncScroll
}) => {
  return (
    <main className="reader-content">
      <div className="reader-book-layout">
        <div className="reader-pane">
          <div className="pane-header-sticky">{t.preview_original}</div>
          <div className="image-scroll-wrapper" ref={scrollRefOrig} onScroll={handleSyncScroll('orig')}>
            {displaySrc.orig && (
              <img 
                src={displaySrc.orig} 
                alt="Original" 
                className={`reader-image ${isPreloading ? 'loading' : ''}`} 
                style={{ width: `${zoom}%`, maxWidth: 'none' }}
              />
            )}
          </div>
        </div>

        <div className="reader-pane">
          <div className="pane-header-sticky">{t.preview_translated}</div>
          <div className="image-scroll-wrapper" ref={scrollRefTrans} onScroll={handleSyncScroll('trans')}>
            {displaySrc.trans && (
              <img 
                src={displaySrc.trans} 
                alt="Translated" 
                className={`reader-image ${isPreloading ? 'loading' : ''}`} 
                style={{ width: `${zoom}%`, maxWidth: 'none' }}
              />
            )}
          </div>
        </div>
      </div>
    </main>
  );
};
