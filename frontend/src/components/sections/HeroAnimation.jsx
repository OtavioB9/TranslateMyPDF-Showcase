import { useEffect, useState, useRef, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const CONVERSATIONS = [
  {
    file: 'report',
    en: [
      'The architecture of modern',
      'systems requires careful',
      'planning and robust',
      'design patterns to ensure',
      'scalability across layers.',
    ],
    pt: [
      'A arquitetura dos sistemas',
      'modernos exige um',
      'planejamento cuidadoso e',
      'padrões robustos de design',
      'para garantir escalabilidade.',
    ],
  },
  {
    file: 'thesis',
    en: [
      'Machine learning models',
      'demonstrate significant',
      'improvements when trained',
      'with diverse datasets and',
      'proper regularization.',
    ],
    pt: [
      'Modelos de aprendizado de',
      'máquina demonstram melhorias',
      'significativas quando treinados',
      'com dados diversos e',
      'regularização adequada.',
    ],
  },
  {
    file: 'manual',
    en: [
      'Before starting the device',
      'ensure all connections are',
      'properly secured and the',
      'power supply meets the',
      'required specifications.',
    ],
    pt: [
      'Antes de iniciar o dispositivo',
      'certifique-se de que todas as',
      'conexões estão devidamente',
      'fixadas e a fonte de energia',
      'atende às especificações.',
    ],
  },
  {
    file: 'paper',
    en: [
      'The results suggest that',
      'quantum computing will',
      'revolutionize encryption',
      'methods within the next',
      'decade of research.',
    ],
    pt: [
      'Os resultados sugerem que a',
      'computação quântica irá',
      'revolucionar os métodos de',
      'criptografia na próxima',
      'década de pesquisa.',
    ],
  },
  {
    file: 'contract',
    en: [
      'Both parties agree to the',
      'terms outlined in section',
      'three regarding payment',
      'schedules and delivery',
      'milestones for the project.',
    ],
    pt: [
      'Ambas as partes concordam',
      'com os termos descritos na',
      'seção três sobre cronogramas',
      'de pagamento e marcos de',
      'entrega do projeto.',
    ],
  },
]

const LINE_WIDTHS = ['94%', '84%', '72%', '90%', '80%']
const SPEED_FAST = 0.035
const SPEED_SLOW = 0.035
const LINE_PAUSE = 0.05

function TypewriterLine({ text, speed = SPEED_FAST, delay = 0, isCurrent = false, active = true, className = "" }) {
  const [displayText, setDisplayText] = useState('')
  
  useEffect(() => {
    if (!active) {
      setDisplayText('')
      return
    }

    const timeout = setTimeout(() => {
      let i = 0
      const interval = setInterval(() => {
        if (i <= text.length) {
          setDisplayText(text.slice(0, i))
          i++
        } else {
          clearInterval(interval)
        }
      }, speed * 1000)
      return () => clearInterval(interval)
    }, delay * 1000)

    return () => clearTimeout(timeout)
  }, [text, speed, delay, active])

  return (
    <span className={`doc-line-text ${className}`}>
      {displayText}
      {isCurrent && (
        <motion.span
          className="typing-cursor"
          animate={{ opacity: [1, 0, 1] }}
          transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
          style={{
            display: 'inline-block',
            width: '2px',
            height: '1.1em',
            background: 'currentColor',
            marginLeft: '1px',
            verticalAlign: 'middle',
            boxShadow: '0 0 4px currentColor'
          }}
        />
      )}
    </span>
  )
}

export default function HeroAnimation({ siteLang = 'pt' }) {
  const isReverse = siteLang === 'en';
  const [translatedCount, setTranslatedCount] = useState(0)
  const [convIndex, setConvIndex] = useState(0)
  const [isTranslating, setIsTranslating] = useState(false)
  const [phase, setPhase] = useState('typing')
  const [activeLineIndex, setActiveLineIndex] = useState(0)
  const timeouts = useRef([])

  const conv = CONVERSATIONS[convIndex]

  const originalStats = useMemo(() => {
    const texts = isReverse ? conv.pt : conv.en
    let currentDelay = 0
    return texts.map(text => {
      const start = currentDelay
      const duration = (text.length * SPEED_FAST)
      currentDelay += duration + LINE_PAUSE
      return { start, duration, total: start + duration }
    })
  }, [conv, isReverse])

  const totalTypingTime = originalStats[originalStats.length - 1].total

  const clear = useCallback(() => {
    timeouts.current.forEach(clearTimeout)
    timeouts.current = []
  }, [])

  useEffect(() => {
    const runCycle = () => {
      clear()
      
      setPhase('typing')
      setTranslatedCount(0)
      setIsTranslating(false)
      setActiveLineIndex(0)

      originalStats.forEach((stats, i) => {
        timeouts.current.push(
          setTimeout(() => setActiveLineIndex(i), stats.start * 1000)
        )
      })

      timeouts.current.push(
        setTimeout(() => {
          setPhase('waiting')
          setActiveLineIndex(-1)
        }, totalTypingTime * 1000 + 100)
      )

      timeouts.current.push(
        setTimeout(() => {
          setPhase('translating')
          setIsTranslating(true)
          
          let cumulativeTranslateTime = 0
          const ptTexts = isReverse ? conv.en : conv.pt
          
          for (let i = 0; i < 5; i++) {
            const lineTime = (ptTexts[i].length * SPEED_SLOW * 1000) + 100
            
            timeouts.current.push(
              setTimeout(() => {
                setTranslatedCount(i + 1)
                setActiveLineIndex(i)
              }, cumulativeTranslateTime)
            )
            cumulativeTranslateTime += lineTime
          }

          timeouts.current.push(
            setTimeout(() => {
              setIsTranslating(false)
              setPhase('result')
              setActiveLineIndex(-1)
            }, cumulativeTranslateTime + 300)
          )

          timeouts.current.push(
            setTimeout(() => {
              setConvIndex(prev => (prev + 1) % CONVERSATIONS.length)
            }, cumulativeTranslateTime + 1500)
          )

        }, totalTypingTime * 1000 + 400)
      )
    }

    runCycle()
    return () => clear()
  }, [clear, totalTypingTime, convIndex, originalStats, isReverse, siteLang])

  return (
    <div className="hero-3d-scene">
      <AnimatePresence mode="wait" initial={true}>
        <motion.div
          key={`${convIndex}-${siteLang}`}
          className="hero-3d-document"
          initial={{ opacity: 0, x: 240, rotateY: 15, scale: 0.95 }}
          animate={{
            opacity: 1,
            x: 0,
            y: [0, -10, 0],
            rotateY: isTranslating ? 6 : 0,
            rotateX: -5,
            scale: isTranslating ? 0.98 : 1,
          }}
          exit={{ 
            opacity: 0, 
            scale: 0.8,
            x: -20,
            filter: "blur(10px)",
            transition: { duration: 0.4, ease: "easeIn" } 
          }}
          transition={{ 
            y: { repeat: Infinity, duration: 5, ease: "easeInOut" },
            default: { type: "spring", stiffness: 50, damping: 20, mass: 1 }
          }}
        >
          <div className="doc-header">
            <div className="doc-dots">
              <span /><span /><span />
            </div>
            <div className="doc-title-bar">
              <motion.span className="doc-filename" animate={{ opacity: 0.5 }}>
                {conv.file}_{translatedCount >= 5 ? (isReverse ? 'en' : 'pt') : (isReverse ? 'pt' : 'en')}.pdf
              </motion.span>
            </div>
          </div>

          <div className="doc-body">
            {conv.en.map((_, i) => {
              const isLineTranslated = i < translatedCount
              const enText = isReverse ? conv.pt[i] : conv.en[i]
              const ptText = isReverse ? conv.en[i] : conv.pt[i]
              const isCurrent = activeLineIndex === i

              return (
                <div key={`line-${i}`} className={`doc-line ${isLineTranslated ? 'pt-line' : 'en-line'}`} style={{ width: LINE_WIDTHS[i] }}>
                  <AnimatePresence mode="wait">
                    {!isLineTranslated ? (
                      <TypewriterLine 
                        key="en"
                        text={enText} 
                        speed={SPEED_FAST}
                        delay={originalStats[i].start} 
                        isCurrent={isCurrent}
                        active={phase !== 'result'} 
                        className="en-text" 
                      />
                    ) : (
                      <TypewriterLine 
                        key="pt"
                        text={ptText} 
                        speed={SPEED_SLOW}
                        delay={0} 
                        isCurrent={isCurrent}
                        active={true} 
                        className="pt-text" 
                      />
                    )}
                  </AnimatePresence>
                </div>
              )
            })}
          </div>

          <div className="doc-footer">
            <motion.span
              className={`lang-badge ${translatedCount >= 5 ? 'pt' : 'en'}`}
              animate={{ scale: isTranslating ? [1, 1.05, 1] : 1 }}
              transition={{ duration: 0.6, repeat: isTranslating ? Infinity : 0, repeatDelay: 0.3 }}
            >
              {translatedCount >= 5 ? (isReverse ? 'EN-US' : 'PT-BR') : (isReverse ? 'PT-BR' : 'EN')}
            </motion.span>

            <div className="translate-progress">
              {[0, 1, 2, 3, 4].map(i => (
                <motion.span
                  key={i}
                  className="progress-dot"
                  animate={{
                    background: i < translatedCount ? 'var(--accent-rose)' : 'var(--border-hover)',
                    scale: i < translatedCount ? [1, 1.3, 1] : 1,
                  }}
                  transition={{ duration: 0.3, delay: 0.05 }}
                />
              ))}
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
