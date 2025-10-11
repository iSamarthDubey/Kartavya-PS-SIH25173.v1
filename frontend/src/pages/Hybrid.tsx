import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { Helmet } from 'react-helmet-async'

import HybridConsole from '@/components/Hybrid/HybridConsole'
import { useAppStore } from '@/stores/appStore'

export default function Hybrid() {
  const setMode = useAppStore(state => state.setMode)

  useEffect(() => {
    setMode('hybrid')
  }, [setMode])

  return (
    <>
      <Helmet>
        <title>Hybrid Mode - SYNRGY</title>
        <meta name="description" content="Unified dashboard and chat interface for comprehensive cybersecurity intelligence" />
      </Helmet>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="h-full overflow-hidden"
      >
        <HybridConsole className="w-full h-full" />
      </motion.div>
    </>
  )
}
