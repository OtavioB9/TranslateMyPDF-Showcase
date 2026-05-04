import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, Check } from 'lucide-react'
import './CustomSelect.css'

export default function CustomSelect({ value, onChange, options, disabled }) {
  const [isOpen, setIsOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    function handleClickOutside(event) {
      if (ref.current && !ref.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const selectedOption = options.find(o => o.value === value)

  return (
    <div className={`custom-select-container ${disabled ? 'disabled' : ''}`} ref={ref}>
      <div 
        className={`custom-select-trigger ${isOpen ? 'open' : ''}`} 
        onClick={() => !disabled && setIsOpen(!isOpen)}
      >
        <span>{selectedOption?.label}</span>
        {!disabled && <ChevronDown size={14} className={`custom-select-icon ${isOpen ? 'rotated' : ''}`} />}
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div 
            className="custom-select-dropdown"
            initial={{ opacity: 0, y: 5, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 5, scale: 0.98 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
          >
            {options.map((option) => (
              <div 
                key={option.value}
                className={`custom-select-option ${value === option.value ? 'selected' : ''}`}
                onClick={() => {
                  onChange(option.value)
                  setIsOpen(false)
                }}
              >
                <span>{option.label}</span>
                {value === option.value && <Check size={14} className="check-icon" />}
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
