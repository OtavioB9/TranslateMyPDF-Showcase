import { useState, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import { motion, useMotionValue, animate, useDragControls } from 'framer-motion'
import './PdfPreview.css'
import { PdfPreviewHeader } from './PdfPreviewHeader'
import { PdfPreviewNavigation } from './PdfPreviewNavigation'
import { PdfPreviewContent } from './PdfPreviewContent'
import { PdfPreviewOverlay } from './PdfPreviewOverlay'
import { transitionVariants } from './variants'

export function PdfPreview({ jobId, apiBase, t, status, limitPages, mode = 'single' }) {
  const [pageCount, setPageCount] = useState(0)
  const [showOriginal, setShowOriginal] = useState(false)
  const dragX = useMotionValue(0)
  const expandedDragX = useMotionValue(0)
  const [[currentPage, direction, actionType], setPage] = useState([0, 0, 'paginate'])
  const [isExpanded, setIsExpanded] = useState(false)
  const [zoom, setZoom] = useState(1)
  const leftScrollRef = useRef(null)
  const rightScrollRef = useRef(null)
  const [showDownloadMenu, setShowDownloadMenu] = useState(false)
  const [pageRange, setPageRange] = useState('')
  const [mousePos, setMousePos] = useState({ x: 0.5, y: 0.5 })
  const dragControls = useDragControls()
  const [displaySrc, setDisplaySrc] = useState(null)
  const [displaySrcSide, setDisplaySrcSide] = useState({ orig: null, trans: null })
  const [isPreloading, setIsPreloading] = useState(true)
  const [showSpinner, setShowSpinner] = useState(false)
  
  const viewerRef = useRef(null)
  const lastTapTime = useRef(0)

  const targetSrc = `${apiBase}/preview/${jobId}/${currentPage}?version=${showOriginal ? 'original' : 'translated'}`
  const targetSrcOrig = `${apiBase}/preview/${jobId}/${currentPage}?version=original`
  const targetSrcTrans = `${apiBase}/preview/${jobId}/${currentPage}?version=translated`

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const res = await fetch(`${apiBase}/preview/${jobId}/info?t=${Date.now()}`)
        const data = await res.json()
        let count = data.page_count
        if (limitPages && !isNaN(limitPages)) {
          count = Math.min(count, parseInt(limitPages))
        }
        setPageCount(count)
      } catch (err) {
        console.error('Preview info error:', err)
      }
    }
    fetchInfo()
  }, [jobId, apiBase, status, limitPages])

  useEffect(() => {
    let isCancelled = false
    setIsPreloading(true)
    
    if (mode === 'side') {
      let loadedCount = 0
      const checkDone = () => {
        loadedCount++
        if (loadedCount === 2 && !isCancelled) {
          setDisplaySrcSide({ orig: targetSrcOrig, trans: targetSrcTrans })
          setIsPreloading(false)
        }
      }
      const img1 = new Image(); img1.onload = checkDone; img1.onerror = checkDone; img1.src = targetSrcOrig;
      const img2 = new Image(); img2.onload = checkDone; img2.onerror = checkDone; img2.src = targetSrcTrans;
    } else {
      const img = new Image()
      img.onload = () => {
        if (!isCancelled) {
          setDisplaySrc(targetSrc)
          setIsPreloading(false)
          if (viewerRef.current && actionType === 'paginate') {
            viewerRef.current.scrollTop = 0
          }
        }
      }
      img.onerror = () => {
        if (!isCancelled) {
          setIsPreloading(false)
        }
      }
      img.src = targetSrc
    }

    return () => {
      isCancelled = true
    }
  }, [targetSrc, targetSrcOrig, targetSrcTrans, actionType, mode])

  useEffect(() => {
    if (isPreloading) {
      const timer = setTimeout(() => setShowSpinner(true), 150)
      return () => clearTimeout(timer)
    } else {
      setShowSpinner(false)
    }
  }, [isPreloading])

  useEffect(() => {
    if (pageCount === 0) return
    const isMobile = window.innerWidth <= 768;
    const timer = setTimeout(() => {
      const preload = (pIndex, orig) => {
        const src = `${apiBase}/preview/${jobId}/${pIndex}?version=${orig ? 'original' : 'translated'}`
        const img = new Image()
        img.src = src
      }
      if (currentPage < pageCount - 1) preload(currentPage + 1, showOriginal)
      if (!isMobile) {
        if (currentPage > 0) preload(currentPage - 1, showOriginal)
        preload(currentPage, !showOriginal)
      }
    }, 400);
    return () => clearTimeout(timer);
  }, [currentPage, showOriginal, pageCount, jobId, apiBase])

  useEffect(() => {
    const timer = setTimeout(() => {
      if (isExpanded && currentPage < pageCount - 1) {
        const nextP = currentPage + 1
        const p1 = new Image(); p1.src = `${apiBase}/preview/${jobId}/${nextP}?version=original`
        if (window.innerWidth > 768) {
          const p2 = new Image(); p2.src = `${apiBase}/preview/${jobId}/${nextP}?version=translated`
        }
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [isExpanded, currentPage, pageCount, jobId, apiBase])

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === 'Escape') setIsExpanded(false)
      if (isExpanded) {
        if (e.key === 'ArrowRight' && currentPage < pageCount - 1) paginate(1)
        if (e.key === 'ArrowLeft' && currentPage > 0) paginate(-1)
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [isExpanded, currentPage, pageCount])


  const handleMouseMove = (e) => {
    if (zoom <= 1) return
    const rect = e.currentTarget.getBoundingClientRect()
    const x = (e.clientX - rect.left) / rect.width
    const y = (e.clientY - rect.top) / rect.height
    setMousePos({ x, y })
  }

  const paginate = (newDirection) => {
    if (isPreloading) return
    dragX.set(0)
    expandedDragX.set(0)
    setZoom(1) 
    
    if (leftScrollRef.current) leftScrollRef.current.scrollTop = 0
    if (rightScrollRef.current) rightScrollRef.current.scrollTop = 0
    
    setPage([currentPage + newDirection, newDirection, 'paginate'])
  }

  const syncScroll = (e) => {
    const source = e.target
    const target = source === leftScrollRef.current ? rightScrollRef.current : leftScrollRef.current
    if (target) {
      target.scrollTop = source.scrollTop
      target.scrollLeft = source.scrollLeft
    }
  }

  const handleDragEnd = (event, info) => {
    const threshold = 100
    if (info.offset.x > threshold && currentPage > 0) {
      paginate(-1)
    } else if (info.offset.x < -threshold && currentPage < pageCount - 1) {
      paginate(1)
    } else {
      animate(expandedDragX, 0, { type: 'spring', stiffness: 300, damping: 30 })
    }
  }

  const handleDownload = () => {
    window.open(`${apiBase}/download/${jobId}?t=${Date.now()}`, '_blank')
    setShowDownloadMenu(false)
  }

  const handleRangeDownload = (e) => {
    e.preventDefault()
    if (!pageRange.trim()) return
    window.open(`${apiBase}/download/${jobId}?range=${encodeURIComponent(pageRange)}&t=${Date.now()}`, '_blank')
    setShowDownloadMenu(false)
  }

  const toggleVersion = () => {
    if (isPreloading) return
    setPage([currentPage, showOriginal ? -1 : 1, 'toggle']) 
    setShowOriginal(v => !v)
  }

  const isSide = mode === 'side'

  return (
    <div className={`preview-container ${isSide ? 'side-mode' : 'single-mode'}`}>
      <PdfPreviewHeader 
        isSide={isSide}
        t={t}
        showOriginal={showOriginal}
        toggleVersion={toggleVersion}
        isPreloading={isPreloading}
        setIsExpanded={setIsExpanded}
        setZoom={setZoom}
      />

      <PdfPreviewContent 
        isSide={isSide}
        viewerRef={viewerRef}
        setIsExpanded={setIsExpanded}
        showSpinner={showSpinner}
        displaySrc={displaySrc}
        direction={direction}
        actionType={actionType}
        dragX={dragX}
        currentPage={currentPage}
        pageCount={pageCount}
        paginate={paginate}
        lastTapTime={lastTapTime}
        displaySrcSide={displaySrcSide}
        apiBase={apiBase}
        jobId={jobId}
        showOriginal={showOriginal}
        t={t}
      />

      <PdfPreviewNavigation 
        pageCount={pageCount}
        currentPage={currentPage}
        paginate={paginate}
        isPreloading={isPreloading}
      />

      <PdfPreviewOverlay 
        isExpanded={isExpanded}
        setIsExpanded={setIsExpanded}
        t={t}
        currentPage={currentPage}
        pageCount={pageCount}
        mode={mode}
        toggleVersion={toggleVersion}
        showOriginal={showOriginal}
        showDownloadMenu={showDownloadMenu}
        setShowDownloadMenu={setShowDownloadMenu}
        handleDownload={handleDownload}
        pageRange={pageRange}
        setPageRange={setPageRange}
        handleRangeDownload={handleRangeDownload}
        setZoom={setZoom}
        expandedDragX={expandedDragX}
        handleDragEnd={handleDragEnd}
        leftScrollRef={leftScrollRef}
        rightScrollRef={rightScrollRef}
        syncScroll={syncScroll}
        handleMouseMove={handleMouseMove}
        zoom={zoom}
        mousePos={mousePos}
        jobId={jobId}
        apiBase={apiBase}
        paginate={paginate}
        direction={direction}
        actionType={actionType}
        displaySrc={displaySrc}
        displaySrcSide={displaySrcSide}
      />
    </div>
  )
}

export default PdfPreview;
