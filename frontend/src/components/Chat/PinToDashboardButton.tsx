import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Pin, 
  PinOff, 
  LayoutDashboard, 
  Settings, 
  ChevronDown,
  Check,
  X,
  Sparkles
} from 'lucide-react'

import { useHybridStore } from '../../stores/hybridStore'
import type { VisualPayload, ChatMessage } from '../../types'

interface PinToDashboardButtonProps {
  message: ChatMessage
  visualPayload: VisualPayload
  className?: string
}

export default function PinToDashboardButton({ 
  message, 
  visualPayload, 
  className = '' 
}: PinToDashboardButtonProps) {
  const [showOptions, setShowOptions] = useState(false)
  const [customTitle, setCustomTitle] = useState('')
  const [selectedCards, setSelectedCards] = useState<string[]>([])
  
  const { 
    pendingPinRequests,
    pinnedWidgets,
    addPendingPin,
    confirmPin,
    cancelPin,
    generateWidgetFromPayload,
    setHybridMode
  } = useHybridStore()
  
  const isPending = message.id in pendingPinRequests
  const isAlreadyPinned = pinnedWidgets.some(w => w.id.includes(message.id))

  // Get pinnable cards from composite payload
  const getPinnableCards = () => {
    if (visualPayload.type === 'composite' && visualPayload.cards) {
      return visualPayload.cards.map((card, index) => ({
        id: `card_${index}`,
        title: card.title || `${card.type} ${index + 1}`,
        type: card.type,
        selected: selectedCards.includes(`card_${index}`)
      }))
    }
    return []
  }

  const handleQuickPin = () => {
    if (isPending || isAlreadyPinned) return
    
    // Quick pin with default settings
    const widget = generateWidgetFromPayload(visualPayload, message.id)
    confirmPin(message.id, {
      title: customTitle || widget.title,
      id: `widget_${message.id}_${Date.now()}`
    })
    
    // Switch to hybrid mode to show the pinned widget
    setHybridMode(true)
  }

  const handleCustomPin = () => {
    if (isPending || isAlreadyPinned) return
    
    let payloadToPin = visualPayload
    
    // If specific cards are selected, create a filtered payload
    if (selectedCards.length > 0 && visualPayload.type === 'composite' && visualPayload.cards) {
      const selectedCardIndices = selectedCards.map(id => parseInt(id.split('_')[1]))
      payloadToPin = {
        ...visualPayload,
        cards: visualPayload.cards.filter((_, index) => selectedCardIndices.includes(index))
      }
    }
    
    const widget = generateWidgetFromPayload(payloadToPin, message.id)
    confirmPin(message.id, {
      title: customTitle || widget.title,
      id: `widget_${message.id}_${Date.now()}`
    })
    
    setShowOptions(false)
    setCustomTitle('')
    setSelectedCards([])
    
    // Switch to hybrid mode
    setHybridMode(true)
  }

  const handleCancelPin = () => {
    cancelPin(message.id)
    setShowOptions(false)
    setCustomTitle('')
    setSelectedCards([])
  }

  const toggleCardSelection = (cardId: string) => {
    setSelectedCards(prev => 
      prev.includes(cardId) 
        ? prev.filter(id => id !== cardId)
        : [...prev, cardId]
    )
  }

  if (isAlreadyPinned) {
    return (
      <div className={`flex items-center gap-2 text-xs text-synrgy-accent ${className}`}>
        <PinOff className="w-3 h-3" />
        <span>Pinned to Dashboard</span>
      </div>
    )
  }

  return (
    <div className={`relative ${className}`}>
      {!isPending && !showOptions && (
        <div className="flex items-center gap-2">
          <button
            onClick={handleQuickPin}
            className="flex items-center gap-1 px-2 py-1 text-xs rounded-lg bg-synrgy-primary/10 text-synrgy-primary hover:bg-synrgy-primary/20 transition-colors"
            title="Pin to dashboard"
          >
            <Pin className="w-3 h-3" />
            <span>Pin to Dashboard</span>
          </button>
          
          <button
            onClick={() => setShowOptions(true)}
            className="p-1 rounded text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 transition-colors"
            title="Pin options"
          >
            <ChevronDown className="w-3 h-3" />
          </button>
        </div>
      )}

      {isPending && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-2 px-2 py-1 bg-synrgy-accent/10 border border-synrgy-accent/20 rounded-lg"
        >
          <div className="flex items-center gap-1 text-xs text-synrgy-accent">
            <Sparkles className="w-3 h-3 animate-pulse" />
            <span>Pinning...</span>
          </div>
          
          <button
            onClick={handleCancelPin}
            className="p-0.5 rounded text-synrgy-muted hover:text-red-400 transition-colors"
            title="Cancel pin"
          >
            <X className="w-3 h-3" />
          </button>
        </motion.div>
      )}

      {/* Pin Options Panel */}
      <AnimatePresence>
        {showOptions && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            className="absolute top-full left-0 mt-2 bg-synrgy-surface border border-synrgy-primary/20 rounded-xl shadow-xl z-50 min-w-80"
          >
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-synrgy-text flex items-center gap-2">
                  <LayoutDashboard className="w-4 h-4" />
                  Pin to Dashboard
                </h3>
                <button
                  onClick={() => setShowOptions(false)}
                  className="p-1 rounded text-synrgy-muted hover:text-synrgy-primary transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-4">
                {/* Custom Title Input */}
                <div>
                  <label className="block text-sm font-medium text-synrgy-text mb-2">
                    Widget Title
                  </label>
                  <input
                    type="text"
                    value={customTitle}
                    onChange={(e) => setCustomTitle(e.target.value)}
                    placeholder="Enter custom title (optional)"
                    className="w-full px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg text-synrgy-text placeholder:text-synrgy-muted focus:border-synrgy-primary/50 outline-none"
                  />
                </div>

                {/* Card Selection for Composite Payloads */}
                {visualPayload.type === 'composite' && visualPayload.cards && visualPayload.cards.length > 1 && (
                  <div>
                    <label className="block text-sm font-medium text-synrgy-text mb-2">
                      Select Components to Pin
                    </label>
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                      {getPinnableCards().map((card) => (
                        <label
                          key={card.id}
                          className="flex items-center gap-3 p-2 rounded-lg hover:bg-synrgy-primary/10 cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedCards.includes(card.id)}
                            onChange={() => toggleCardSelection(card.id)}
                            className="w-4 h-4 text-synrgy-primary bg-synrgy-bg-900 border-synrgy-primary/20 rounded focus:ring-synrgy-primary/20"
                          />
                          <div className="flex-1">
                            <div className="text-sm text-synrgy-text">{card.title}</div>
                            <div className="text-xs text-synrgy-muted capitalize">{card.type}</div>
                          </div>
                        </label>
                      ))}
                    </div>
                    <div className="text-xs text-synrgy-muted mt-2">
                      {selectedCards.length === 0 
                        ? 'All components will be pinned' 
                        : `${selectedCards.length} of ${visualPayload.cards.length} components selected`
                      }
                    </div>
                  </div>
                )}

                {/* Preview Info */}
                <div className="bg-synrgy-bg-900/50 rounded-lg p-3">
                  <div className="text-sm text-synrgy-text mb-1">Preview:</div>
                  <div className="text-xs text-synrgy-muted">
                    <div>Title: {customTitle || 'Auto-generated from content'}</div>
                    <div>Type: {visualPayload.type === 'composite' ? 'Multi-component widget' : `${visualPayload.type} widget`}</div>
                    {visualPayload.type === 'composite' && (
                      <div>
                        Components: {selectedCards.length === 0 
                          ? visualPayload.cards?.length || 0
                          : selectedCards.length
                        }
                      </div>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-3 pt-4">
                  <button
                    onClick={handleCustomPin}
                    className="flex-1 px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg font-medium hover:bg-synrgy-primary/90 transition-colors flex items-center justify-center gap-2"
                  >
                    <Pin className="w-4 h-4" />
                    Pin to Dashboard
                  </button>
                  <button
                    onClick={() => setShowOptions(false)}
                    className="px-4 py-2 text-synrgy-muted hover:text-synrgy-text transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Backdrop for options panel */}
      {showOptions && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowOptions(false)}
        />
      )}
    </div>
  )
}
