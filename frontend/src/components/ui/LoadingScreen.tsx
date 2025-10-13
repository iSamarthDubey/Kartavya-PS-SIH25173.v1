import { motion } from 'framer-motion'

interface LoadingScreenProps {
  message?: string
  subMessage?: string
}

export default function LoadingScreen({ message = 'Loading...', subMessage }: LoadingScreenProps) {
  return (
    <div className="fixed inset-0 bg-synrgy-bg-900 flex items-center justify-center z-50">
      <div className="text-center">
        {/* SYNRGY Logo Animation */}
        <div className="mb-8">
          <motion.div
            className="inline-block"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          >
            <div className="relative">
              {/* Main logo glow effect */}
              <motion.div
                className="absolute inset-0 bg-synrgy-primary/20 rounded-full blur-xl"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.3, 0.6, 0.3],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />

              {/* Logo text */}
              <motion.div
                className="relative z-10 text-6xl md:text-7xl font-heading font-bold text-gradient"
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.8, ease: 'backOut' }}
              >
                SYNRGY
              </motion.div>
            </div>
          </motion.div>

          {/* Subtitle */}
          <motion.p
            className="mt-4 text-synrgy-muted text-lg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            Human + AI. In Perfect SYNRGY.
          </motion.p>
        </div>

        {/* Loading animation */}
        <div className="mb-6">
          <motion.div
            className="flex justify-center space-x-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            {[0, 1, 2].map(i => (
              <motion.div
                key={i}
                className="w-3 h-3 bg-synrgy-primary rounded-full"
                animate={{
                  y: [0, -10, 0],
                  opacity: [0.4, 1, 0.4],
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  delay: i * 0.2,
                }}
              />
            ))}
          </motion.div>
        </div>

        {/* Messages */}
        <motion.div
          className="space-y-2"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.4 }}
        >
          <p className="text-synrgy-text font-medium">{message}</p>

          {subMessage && <p className="text-synrgy-muted text-sm">{subMessage}</p>}
        </motion.div>

        {/* Progress bar */}
        <motion.div
          className="mt-8 w-64 mx-auto"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <div className="h-1 bg-synrgy-surface rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-synrgy-primary to-synrgy-accent rounded-full"
              animate={{
                x: ['-100%', '100%'],
                opacity: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          </div>
        </motion.div>
      </div>
    </div>
  )
}
