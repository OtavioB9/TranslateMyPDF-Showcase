import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import './PdfReader.css'
import { PdfReaderHeader } from './PdfReaderHeader'
import { PdfReaderContent } from './PdfReaderContent'
import { PdfReaderControls } from './PdfReaderControls'

export default function PdfReader({ jobId, apiBase, t, onClose, initialPage = 0 }) {
  const [currentPage, setCurrentPage] = useState(initialPage)
  const [pageCount, setPageCount] = useState(0)
  const [isPreloading, setIsPreloading] = useState(true)
  const [displaySrc, setDisplaySrc] = useState({ orig: null, trans: null })
  const [zoom, setZoom] = useState(100)
  const [isSyncing, setIsSyncing] = useState(true)
  
  const scrollRefOrig = useRef(null)
  const scrollRefTrans = useRef(null)
  const activeScroll = useRef(null)

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const res = await fetch(`${apiBase}/preview/${jobId}/info`)
        const data = await res.json()
        setPageCount(data.page_count)
      } catch (err) {
        console.error('Reader info error:', err)
      }
    }
    fetchInfo()
  }, [jobId, apiBase])

  useEffect(() => {
    setIsPreloading(true)
    const targetOrig = `${apiBase}/preview/${jobId}/${currentPage}?version=original`
    const targetTrans = `${apiBase}/preview/${jobId}/${currentPage}?version=translated`
    
    let loaded = 0
    const checkDone = () => {
      loaded++
      if (loaded === 2) {
        setDisplaySrc({ orig: targetOrig, trans: targetTrans })
        setIsPreloading(false)
        if (scrollRefOrig.current) scrollRefOrig.current.scrollTop = 0
        if (scrollRefTrans.current) scrollRefTrans.current.scrollTop = 0
      }
    }

    const img1 = new Image(); img1.onload = checkDone; img1.src = targetOrig
    const img2 = new Image(); img2.onload = checkDone; img2.src = targetTrans
  }, [currentPage, jobId, apiBase])

  const handleSyncScroll = (source) => (e) => {
    if (!isSyncing) return
    if (activeScroll.current && activeScroll.current !== source) return

    activeScroll.current = source
    const { scrollTop } = e.target
    const target = source === 'orig' ? scrollRefTrans.current : scrollRefOrig.current
    
    if (target) {
      target.scrollTop = scrollTop
    }

    window.syncTimeout = setTimeout(() => {
      activeScroll.current = null
    }, 50)
  }

  const handleDownload = async () => {
    try {
      const res = await fetch(`${apiBase}/download/${jobId}`)
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `translated_${jobId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Download error:', err)
    }
  }

  return (
    <motion.div 
      className="pdf-reader-view"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <PdfReaderHeader 
        t={t}
        currentPage={currentPage}
        pageCount={pageCount}
        setCurrentPage={setCurrentPage}
        handleDownload={handleDownload}
        onClose={onClose}
      />

      <PdfReaderContent 
        t={t}
        displaySrc={displaySrc}
        isPreloading={isPreloading}
        zoom={zoom}
        scrollRefOrig={scrollRefOrig}
        scrollRefTrans={scrollRefTrans}
        handleSyncScroll={handleSyncScroll}
      />

      <PdfReaderControls 
        zoom={zoom}
        setZoom={setZoom}
        isSyncing={isSyncing}
        setIsSyncing={setIsSyncing}
      />

      {isPreloading && (
        <div className="reader-overlay-loading">
          <div className="reader-spinner" />
        </div>
      )}
    </motion.div>
  )
}
