import { useState, useEffect } from 'react';
import { useSpring, useTransform } from 'framer-motion';
import api from '../services/api';
import { API_BASE } from '../i18n/translations';

export function useTranslation(t) {
  const [fileList, setFileList] = useState([]);
  const [currentFileIndex, setCurrentFileIndex] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const [limitPages, setLimitPages] = useState('');
  const [sourceLang, setSourceLang] = useState('en');
  const [targetLang, setTargetLang] = useState('pt');
  const [isCounting, setIsCounting] = useState(false);
  const [fileTotalPages, setFileTotalPages] = useState(0);
  const [hasStartedTranslation, setHasStartedTranslation] = useState(false);
  const [pageRange, setPageRange] = useState('');
  const [engineOnline, setEngineOnline] = useState(false);
  const [stableEta, setStableEta] = useState(0);
  const [startTime, setStartTime] = useState(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_BASE}/health?t=${Date.now()}`);
        setEngineOnline(res.ok);
      } catch {
        setEngineOnline(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    let interval;
    if (jobId && hasStartedTranslation && status?.status !== 'completed' && status?.status !== 'failed') {
      interval = setInterval(async () => {
        try {
          const res = await api.get(`${API_BASE}/status/${jobId}?_t=${Date.now()}`);
          setStatus(res.data);
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [jobId, hasStartedTranslation, status]);

  const animatedProgress = useSpring(0, { stiffness: 20, damping: 40, restDelta: 0.001 });
  const displayProgress = useTransform(animatedProgress, v => `${Math.round(v)}%`);
  const displayWidth = useTransform(animatedProgress, v => `${v}%`);

  useEffect(() => {
    animatedProgress.set(status?.progress || 0);
  }, [status, animatedProgress]);

  useEffect(() => {
    if (hasStartedTranslation && !startTime && status?.status === 'processing') {
      setStartTime(Date.now());
    }
    if (!hasStartedTranslation || status?.status === 'completed') {
      setStartTime(null);
      setStableEta(0);
    }
  }, [hasStartedTranslation, status?.status]);

  useEffect(() => {
    let interval;
    if (startTime && status?.progress > 0 && status?.progress < 100) {
      interval = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        const progress = status.progress / 100;
        const estimatedTotal = elapsed / progress;
        const remaining = Math.max(0, estimatedTotal - elapsed);

        const serverEta = status.eta || remaining;
        const blended = status.eta 
          ? (remaining * 0.3) + (status.eta * 0.7)
          : remaining;

        setStableEta(Math.ceil(blended));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [startTime, status?.progress, status?.eta]);

  useEffect(() => {
    if (status?.status === 'completed' && hasStartedTranslation) {
      setFileList(prev => {
        const updated = [...prev];
        if (currentFileIndex !== null) {
          updated[currentFileIndex].status = 'completed';
        }
        return updated;
      });

      const nextIdx = fileList.findIndex((f, i) => i > currentFileIndex && f.status !== 'completed');
      if (nextIdx !== -1) {
        setCurrentFileIndex(nextIdx);
        setJobId(fileList[nextIdx].jobId);
        const params = limitPages ? `?limit_pages=${limitPages}` : '';
        api.post(`${API_BASE}/translate/${fileList[nextIdx].jobId}${params}`);
      }
    }
  }, [status, hasStartedTranslation, fileList, currentFileIndex, limitPages]);

  const handleUpload = async (e) => {
    const selectedFiles = Array.from(e.target.files);
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    setError(null);

    const newFiles = selectedFiles.map(f => ({
      file: f,
      id: Math.random().toString(36).substr(2, 9),
      status: 'idle',
      jobId: null,
      totalPages: 0,
      progress: 0
    }));

    const currentFileListLength = fileList.length;
    setFileList(prev => [...prev, ...newFiles]);

    if (currentFileIndex === null) {
      setCurrentFileIndex(currentFileListLength);
    }

    for (let i = 0; i < newFiles.length; i++) {
      const fileObj = newFiles[i];
      const formData = new FormData();
      formData.append('file', fileObj.file);

      try {
        const res = await api.post(`${API_BASE}/upload`, formData);
        const globalIdx = currentFileListLength + i;

        setFileList(prev => {
          const updated = [...prev];
          updated[globalIdx] = {
            ...updated[globalIdx],
            jobId: res.data.job_id,
            totalPages: res.data.total_pages || 0,
            status: 'ready'
          };
          return updated;
        });

        if (globalIdx === (currentFileIndex ?? currentFileListLength)) {
          setJobId(res.data.job_id);
          setFileTotalPages(res.data.total_pages || 0);
          setLimitPages(res.data.total_pages || '');
        }
      } catch (err) {
        console.error("Upload error for file", fileObj.file.name, err);
      }
    }

    setIsUploading(false);
    setIsCounting(true);
    setTimeout(() => {
      setIsCounting(false);
    }, 2500);
  };

  const handleTranslate = async () => {
    setHasStartedTranslation(true);
    for (let i = 0; i < fileList.length; i++) {
      const fileObj = fileList[i];
      if (fileObj.status === 'completed') continue;

      setCurrentFileIndex(i);
      setJobId(fileObj.jobId);

      const params = limitPages ? `?limit_pages=${limitPages}` : '';
      try {
        await api.post(`${API_BASE}/translate/${fileObj.jobId}${params}`);
      } catch {
        setError(t.err_start);
      }
    }
  };

  const resetAll = () => {
    setJobId(null);
    setStatus(null);
    setFileList([]);
    setCurrentFileIndex(null);
    setLimitPages('');
    setError(null);
    setFileTotalPages(0);
    setHasStartedTranslation(false);
    setPageRange('');
  };

  const handleLimitChange = (e) => {
    const val = e.target.value;
    if (val === '') {
      setLimitPages('');
      return;
    }
    const cleanVal = val.replace(/\D/g, '');
    if (cleanVal === '') {
      setLimitPages('');
      return;
    }

    const num = parseInt(cleanVal);
    if (isNaN(num)) return;

    if (num > fileTotalPages) {
      setLimitPages(fileTotalPages);
    } else if (num < 1) {
      setLimitPages(1);
    } else {
      setLimitPages(num);
    }
  };

  const handleKeyDown = (e) => {
    const allowedKeys = ['Delete', 'Backspace', 'Tab', 'Escape', 'Enter',
      'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'];

    if (allowedKeys.includes(e.key)) return;
    if ((e.ctrlKey || e.metaKey) && e.key === 'a') return;

    if (!/^[0-9]$/.test(e.key)) {
      e.preventDefault();
    }
  };

  const handlePageRangeChange = (e) => {
    const val = e.target.value;
    const maxPages = status?.translate_limit || limitPages || fileTotalPages || 0;

    const parts = val.split(/([,\-\s]+)/);
    const validated = parts.map(part => {
      if (/^\d+$/.test(part)) {
        const num = parseInt(part);
        if (num > maxPages) return maxPages.toString();
        return part;
      }
      return part;
    });

    const finalVal = validated.join('').replace(/[^0-9,\-\s]/g, '');
    setPageRange(finalVal);
  };

  return {
    fileList, currentFileIndex, jobId, status, isUploading, error,
    limitPages, sourceLang, targetLang, isCounting, fileTotalPages,
    hasStartedTranslation, pageRange, engineOnline,
    displayProgress, displayWidth, stableEta,
    handleUpload, handleTranslate, resetAll,
    handleLimitChange, handleKeyDown, handlePageRangeChange,
    setSourceLang, setTargetLang, setError
  };
}
