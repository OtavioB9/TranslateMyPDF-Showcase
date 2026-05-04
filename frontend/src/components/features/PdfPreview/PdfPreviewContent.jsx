import React from 'react';
import { motion, AnimatePresence, animate } from 'framer-motion';
import { transitionVariants, sideVariants } from './variants';

export const PdfPreviewContent = ({
  isSide,
  viewerRef,
  setIsExpanded,
  showSpinner,
  displaySrc,
  direction,
  actionType,
  dragX,
  currentPage,
  pageCount,
  paginate,
  lastTapTime,
  displaySrcSide,
  apiBase,
  jobId,
  showOriginal,
  t
}) => {
  return (
    <div 
      className={`preview-viewer-grid ${isSide ? 'side-grid' : ''}`} 
      ref={viewerRef}
      onDoubleClick={() => setIsExpanded(true)}
      style={{ cursor: 'zoom-in' }}
      title="Clique duplo para expandir"
    >
      {!isSide ? (
        <div className="preview-viewer-single">
          {showSpinner && displaySrc && (
            <div className="preview-loading">
              <div className="preview-spinner" />
            </div>
          )}

          <div className="single-preview-wrapper">
            <AnimatePresence mode="wait" custom={{ direction, actionType }}>
              <motion.img
                key={`single-${currentPage}`}
                src={`${apiBase}/preview/${jobId}/${currentPage}?version=${showOriginal ? 'original' : 'translated'}`}
                custom={{ direction, actionType }}
                variants={transitionVariants}
                initial="enter"
                animate="center"
                exit="exit"
                className="preview-image"
                  style={{
                    x: dragX,
                    touchAction: 'none',
                    willChange: 'transform, opacity',
                    transformStyle: 'preserve-3d',
                    backfaceVisibility: 'hidden'
                  }}
                  draggable={false}
                  drag="x"
                  dragConstraints={{ left: 0, right: 0 }}
                  dragElastic={0.2}
                  onDragEnd={(e, { offset }) => {
                    const swipeThreshold = 50;
                    if (offset.x < -swipeThreshold && currentPage < pageCount - 1) {
                      paginate(1);
                    } else if (offset.x > swipeThreshold && currentPage > 0) {
                      paginate(-1);
                    } else {
                      animate(dragX, 0, { type: 'spring', stiffness: 300, damping: 30 });
                    }
                  }}
                  onTap={() => {
                    const now = Date.now();
                    if (now - lastTapTime.current < 300) {
                      setIsExpanded(true);
                    }
                    lastTapTime.current = now;
                  }}
                  alt="PDF Page"
                />
            </AnimatePresence>
          </div>
        </div>
      ) : (
        <div className="side-by-side-layout">
          <div className="side-pane">
            <div className="pane-label">{t.preview_original}</div>
            <div className="pane-content">
              <AnimatePresence mode="wait" custom={{ direction, actionType }}>
                <motion.div
                  key={`orig-${currentPage}`}
                  custom={{ direction, actionType }}
                  variants={transitionVariants}
                  initial="enter"
                  animate="center"
                  exit="exit"
                  style={{
                    position: 'absolute',
                    inset: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <motion.img
                    src={`${apiBase}/preview/${jobId}/${currentPage}?version=original`}
                    className="preview-image"
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'fill',
                      touchAction: 'none',
                      x: dragX,
                      willChange: 'transform, opacity',
                      transformStyle: 'preserve-3d',
                      backfaceVisibility: 'hidden'
                    }}
                    draggable={false}
                    drag="x"
                    dragConstraints={{ left: 0, right: 0 }}
                    dragElastic={0.2}
                    onDragEnd={(e, { offset }) => {
                      const swipeThreshold = 50;
                      if (offset.x < -swipeThreshold && currentPage < pageCount - 1) {
                        paginate(1);
                      } else if (offset.x > swipeThreshold && currentPage > 0) {
                        paginate(-1);
                      } else {
                        animate(dragX, 0, { type: 'spring', stiffness: 300, damping: 30 });
                      }
                    }}
                    alt="Original"
                  />
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
          <div className="side-pane">
            <div className="pane-label">{t.preview_translated}</div>
            <div className="pane-content">
              <AnimatePresence mode="wait" custom={{ direction, actionType }}>
                <motion.div
                  key={`trans-${currentPage}`}
                  custom={{ direction, actionType }}
                  variants={transitionVariants}
                  initial="enter"
                  animate="center"
                  exit="exit"
                  style={{
                    position: 'absolute',
                    inset: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <motion.img
                    src={`${apiBase}/preview/${jobId}/${currentPage}?version=translated`}
                    className="preview-image"
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'fill',
                      touchAction: 'none',
                      x: dragX,
                      willChange: 'transform, opacity',
                      transformStyle: 'preserve-3d',
                      backfaceVisibility: 'hidden'
                    }}
                    draggable={false}
                    drag="x"
                    dragConstraints={{ left: 0, right: 0 }}
                    dragElastic={0.2}
                    onDragEnd={(e, { offset }) => {
                      const swipeThreshold = 50;
                      if (offset.x < -swipeThreshold && currentPage < pageCount - 1) {
                        paginate(1);
                      } else if (offset.x > swipeThreshold && currentPage > 0) {
                        paginate(-1);
                      } else {
                        animate(dragX, 0, { type: 'spring', stiffness: 300, damping: 30 });
                      }
                    }}
                    alt="Translated"
                  />
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
