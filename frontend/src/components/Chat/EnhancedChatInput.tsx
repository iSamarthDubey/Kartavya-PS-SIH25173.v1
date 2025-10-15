/**
 * SYNRGY Enhanced Chat Input
 * Advanced input system with autocomplete, command parsing, and smart suggestions
 */

import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send,
  Mic,
  MicOff,
  Paperclip,
  Command,
  ArrowUp,
  ArrowDown,
  Tab,
  Smile,
  Hash,
  AtSign,
  Calendar,
  Filter,
  Zap,
  Sparkles,
  X,
  Plus,
  Settings,
  History,
  ChevronUp,
  ChevronDown
} from 'lucide-react'

import { 
  TouchButton,
  LoadingSpinner,
  useToast,
  useBreakpoint,
  Tooltip,
  AnimatedCard
} from '@/components/UI'

interface ChatInputProps {
  value?: string
  onChange?: (value: string) => void
  onSend: (message: string, attachments?: File[], metadata?: any) => void
  onVoiceInput?: (audioBlob: Blob) => void
  placeholder?: string
  disabled?: boolean
  maxLength?: number
  suggestions?: string[]
  recentCommands?: string[]
  className?: string
}

interface AutocompleteOption {
  id: string
  type: 'command' | 'entity' | 'suggestion' | 'history'
  value: string
  label: string
  description?: string
  icon?: React.ComponentType<any>
  metadata?: any
}

interface CommandToken {
  type: 'command' | 'parameter' | 'value' | 'operator'
  value: string
  start: number
  end: number
  valid: boolean
}

// Smart Input Component with Autocomplete
export const EnhancedChatInput: React.FC<ChatInputProps> = ({
  value = '',
  onChange,
  onSend,
  onVoiceInput,
  placeholder = "Ask SYNRGY anything...",
  disabled = false,
  maxLength = 2000,
  suggestions = [],
  recentCommands = [],
  className = ''
}) => {
  const [inputValue, setInputValue] = useState(value)
  const [attachments, setAttachments] = useState<File[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [showAutocomplete, setShowAutocomplete] = useState(false)
  const [autocompleteOptions, setAutocompleteOptions] = useState<AutocompleteOption[]>([])
  const [selectedOptionIndex, setSelectedOptionIndex] = useState(-1)
  const [commandTokens, setCommandTokens] = useState<CommandToken[]>([])
  const [cursorPosition, setCursorPosition] = useState(0)
  const [inputHistory, setInputHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [showEmojiPicker, setShowEmojiPicker] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)

  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const autocompleteRef = useRef<HTMLDivElement>(null)
  const { showToast } = useToast()
  const { isMobile } = useBreakpoint()

  // Command parsing patterns
  const COMMAND_PATTERNS = {
    commands: /^\/(\w+)/,
    entities: /@(\w+)/g,
    hashtags: /#(\w+)/g,
    timeframes: /\b(?:last|past|recent)\s+(\d+)\s+(minute|hour|day|week|month)s?\b/g,
    operators: /\b(and|or|not|where|filter|sort|limit)\b/gi
  }

  // Update parent value
  useEffect(() => {
    onChange?.(inputValue)
  }, [inputValue, onChange])

  // Parse command tokens
  const parseCommandTokens = useCallback((input: string): CommandToken[] => {
    const tokens: CommandToken[] = []
    const text = input.toLowerCase()

    // Check for commands
    const commandMatch = text.match(COMMAND_PATTERNS.commands)
    if (commandMatch) {
      tokens.push({
        type: 'command',
        value: commandMatch[1],
        start: commandMatch.index || 0,
        end: (commandMatch.index || 0) + commandMatch[0].length,
        valid: ['show', 'analyze', 'search', 'find', 'generate', 'create'].includes(commandMatch[1])
      })
    }

    // Check for entities
    let entityMatch
    while ((entityMatch = COMMAND_PATTERNS.entities.exec(input)) !== null) {
      tokens.push({
        type: 'parameter',
        value: entityMatch[1],
        start: entityMatch.index,
        end: entityMatch.index + entityMatch[0].length,
        valid: true
      })
    }

    // Check for hashtags (categories/tags)
    let hashtagMatch
    while ((hashtagMatch = COMMAND_PATTERNS.hashtags.exec(input)) !== null) {
      tokens.push({
        type: 'value',
        value: hashtagMatch[1],
        start: hashtagMatch.index,
        end: hashtagMatch.index + hashtagMatch[0].length,
        valid: ['threat', 'alert', 'user', 'network', 'log'].includes(hashtagMatch[1])
      })
    }

    // Check for operators
    let operatorMatch
    while ((operatorMatch = COMMAND_PATTERNS.operators.exec(input)) !== null) {
      tokens.push({
        type: 'operator',
        value: operatorMatch[0].toLowerCase(),
        start: operatorMatch.index,
        end: operatorMatch.index + operatorMatch[0].length,
        valid: true
      })
    }

    return tokens
  }, [])

  // Generate autocomplete options
  const generateAutocompleteOptions = useCallback((input: string, position: number): AutocompleteOption[] => {
    const options: AutocompleteOption[] = []
    const currentWord = input.slice(0, position).split(/\s/).pop() || ''
    const lowerInput = input.toLowerCase()

    // Command suggestions
    if (currentWord.startsWith('/')) {
      const commands = [
        { command: '/show', description: 'Display information about security events' },
        { command: '/analyze', description: 'Perform security analysis on data' },
        { command: '/search', description: 'Search through logs and events' },
        { command: '/find', description: 'Find specific security artifacts' },
        { command: '/generate', description: 'Generate reports and summaries' },
        { command: '/create', description: 'Create dashboards or alerts' }
      ]

      commands.forEach(cmd => {
        if (cmd.command.includes(currentWord.toLowerCase())) {
          options.push({
            id: `cmd-${cmd.command}`,
            type: 'command',
            value: cmd.command + ' ',
            label: cmd.command,
            description: cmd.description,
            icon: Command
          })
        }
      })
    }

    // Entity suggestions
    if (currentWord.startsWith('@')) {
      const entities = [
        { entity: '@user', description: 'User accounts and identities' },
        { entity: '@host', description: 'Network hosts and endpoints' },
        { entity: '@ip', description: 'IP addresses' },
        { entity: '@domain', description: 'Domain names and URLs' },
        { entity: '@file', description: 'Files and file paths' }
      ]

      entities.forEach(ent => {
        if (ent.entity.includes(currentWord.toLowerCase())) {
          options.push({
            id: `entity-${ent.entity}`,
            type: 'entity',
            value: ent.entity + ' ',
            label: ent.entity,
            description: ent.description,
            icon: AtSign
          })
        }
      })
    }

    // Hashtag suggestions
    if (currentWord.startsWith('#')) {
      const hashtags = [
        { tag: '#threat', description: 'Threat-related content' },
        { tag: '#alert', description: 'Security alerts' },
        { tag: '#network', description: 'Network security' },
        { tag: '#user', description: 'User activity' },
        { tag: '#malware', description: 'Malware analysis' },
        { tag: '#compliance', description: 'Compliance and audit' }
      ]

      hashtags.forEach(tag => {
        if (tag.tag.includes(currentWord.toLowerCase())) {
          options.push({
            id: `tag-${tag.tag}`,
            type: 'suggestion',
            value: tag.tag + ' ',
            label: tag.tag,
            description: tag.description,
            icon: Hash
          })
        }
      })
    }

    // Recent commands
    if (recentCommands.length > 0 && currentWord.length > 2) {
      recentCommands.forEach((cmd, index) => {
        if (cmd.toLowerCase().includes(currentWord.toLowerCase())) {
          options.push({
            id: `history-${index}`,
            type: 'history',
            value: cmd,
            label: cmd.length > 60 ? cmd.slice(0, 60) + '...' : cmd,
            description: 'Recent command',
            icon: History
          })
        }
      })
    }

    // General suggestions
    suggestions.forEach((suggestion, index) => {
      if (suggestion.toLowerCase().includes(lowerInput)) {
        options.push({
          id: `suggestion-${index}`,
          type: 'suggestion',
          value: suggestion,
          label: suggestion,
          icon: Sparkles
        })
      }
    })

    return options.slice(0, 10) // Limit to 10 options
  }, [recentCommands, suggestions])

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value
    const position = e.target.selectionStart

    if (newValue.length <= maxLength) {
      setInputValue(newValue)
      setCursorPosition(position)

      // Parse tokens
      const tokens = parseCommandTokens(newValue)
      setCommandTokens(tokens)

      // Generate autocomplete options
      const options = generateAutocompleteOptions(newValue, position)
      setAutocompleteOptions(options)
      setShowAutocomplete(options.length > 0 && newValue.length > 0)
      setSelectedOptionIndex(-1)
    }
  }

  // Handle key events
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Autocomplete navigation
    if (showAutocomplete && autocompleteOptions.length > 0) {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedOptionIndex(prev => 
          prev < autocompleteOptions.length - 1 ? prev + 1 : prev
        )
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedOptionIndex(prev => prev > -1 ? prev - 1 : -1)
      } else if (e.key === 'Tab' || e.key === 'Enter') {
        if (selectedOptionIndex >= 0) {
          e.preventDefault()
          selectAutocompleteOption(autocompleteOptions[selectedOptionIndex])
        }
      } else if (e.key === 'Escape') {
        setShowAutocomplete(false)
        setSelectedOptionIndex(-1)
      }
    }

    // Send message
    if (e.key === 'Enter' && !e.shiftKey && !showAutocomplete) {
      e.preventDefault()
      handleSend()
    }

    // Command history
    if (e.key === 'ArrowUp' && e.ctrlKey) {
      e.preventDefault()
      if (inputHistory.length > 0 && historyIndex < inputHistory.length - 1) {
        const newIndex = historyIndex + 1
        setHistoryIndex(newIndex)
        setInputValue(inputHistory[inputHistory.length - 1 - newIndex])
      }
    } else if (e.key === 'ArrowDown' && e.ctrlKey) {
      e.preventDefault()
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1
        setHistoryIndex(newIndex)
        setInputValue(inputHistory[inputHistory.length - 1 - newIndex])
      } else if (historyIndex === 0) {
        setHistoryIndex(-1)
        setInputValue('')
      }
    }
  }

  // Select autocomplete option
  const selectAutocompleteOption = (option: AutocompleteOption) => {
    const currentWord = inputValue.slice(0, cursorPosition).split(/\s/).pop() || ''
    const beforeCursor = inputValue.slice(0, cursorPosition - currentWord.length)
    const afterCursor = inputValue.slice(cursorPosition)
    
    const newValue = beforeCursor + option.value + afterCursor
    setInputValue(newValue)
    setShowAutocomplete(false)
    setSelectedOptionIndex(-1)

    // Focus back to textarea
    setTimeout(() => {
      textareaRef.current?.focus()
      const newPosition = beforeCursor.length + option.value.length
      textareaRef.current?.setSelectionRange(newPosition, newPosition)
    }, 0)
  }

  // Handle send
  const handleSend = () => {
    if (!inputValue.trim() && attachments.length === 0) return

    // Add to history
    if (inputValue.trim() && !inputHistory.includes(inputValue.trim())) {
      setInputHistory(prev => [inputValue.trim(), ...prev.slice(0, 49)]) // Keep last 50
    }

    // Parse metadata from tokens
    const metadata = {
      tokens: commandTokens,
      hasCommands: commandTokens.some(t => t.type === 'command'),
      entities: commandTokens.filter(t => t.type === 'parameter').map(t => t.value),
      tags: commandTokens.filter(t => t.type === 'value').map(t => t.value)
    }

    onSend(inputValue.trim(), attachments, metadata)
    
    // Reset
    setInputValue('')
    setAttachments([])
    setShowAutocomplete(false)
    setCommandTokens([])
    setHistoryIndex(-1)
  }

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      const scrollHeight = textareaRef.current.scrollHeight
      const maxHeight = isMobile ? 120 : 160
      textareaRef.current.style.height = `${Math.min(scrollHeight, maxHeight)}px`
    }
  }, [inputValue, isMobile])

  // File handling
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setAttachments(prev => [...prev, ...files])
  }

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index))
  }

  // Voice recording
  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false)
      // Stop recording logic
    } else {
      setIsRecording(true)
      // Start recording logic
    }
  }

  // Render highlighted input
  const renderHighlightedInput = () => {
    let highlightedText = inputValue
    const highlights: Array<{start: number, end: number, className: string}> = []

    commandTokens.forEach(token => {
      let className = ''
      switch (token.type) {
        case 'command':
          className = token.valid ? 'text-blue-400 font-semibold' : 'text-red-400'
          break
        case 'parameter':
          className = 'text-green-400'
          break
        case 'value':
          className = token.valid ? 'text-purple-400' : 'text-yellow-400'
          break
        case 'operator':
          className = 'text-orange-400 font-medium'
          break
      }
      
      if (className) {
        highlights.push({
          start: token.start,
          end: token.end,
          className
        })
      }
    })

    return highlights.length > 0 ? (
      <div className="absolute inset-0 pointer-events-none whitespace-pre-wrap break-words p-3 text-transparent">
        {/* Render highlighted spans */}
      </div>
    ) : null
  }

  return (
    <div className={`relative ${className}`}>
      {/* Autocomplete Dropdown */}
      <AnimatePresence>
        {showAutocomplete && autocompleteOptions.length > 0 && (
          <motion.div
            ref={autocompleteRef}
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute bottom-full mb-2 left-0 right-0 max-h-64 overflow-y-auto bg-synrgy-surface border border-synrgy-primary/20 rounded-lg shadow-xl z-50"
          >
            {autocompleteOptions.map((option, index) => (
              <motion.div
                key={option.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`
                  flex items-center gap-3 px-4 py-3 cursor-pointer transition-colors
                  ${index === selectedOptionIndex 
                    ? 'bg-synrgy-primary/20 border-l-2 border-synrgy-primary' 
                    : 'hover:bg-synrgy-primary/5'
                  }
                `}
                onClick={() => selectAutocompleteOption(option)}
              >
                {option.icon && (
                  <option.icon className="w-4 h-4 text-synrgy-primary flex-shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-synrgy-text text-sm">
                      {option.label}
                    </span>
                    <span className="text-xs px-2 py-0.5 bg-synrgy-primary/10 text-synrgy-primary rounded">
                      {option.type}
                    </span>
                  </div>
                  {option.description && (
                    <p className="text-xs text-synrgy-muted mt-1 truncate">
                      {option.description}
                    </p>
                  )}
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Attachments Preview */}
      <AnimatePresence>
        {attachments.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-3 p-3 bg-synrgy-surface/50 rounded-lg border border-synrgy-primary/20"
          >
            <div className="flex flex-wrap gap-2">
              {attachments.map((file, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex items-center gap-2 bg-synrgy-bg-950 rounded-lg px-3 py-2 border border-synrgy-primary/20"
                >
                  <Paperclip className="w-4 h-4 text-synrgy-primary" />
                  <span className="text-sm text-synrgy-text truncate max-w-[200px]">
                    {file.name}
                  </span>
                  <TouchButton
                    variant="ghost"
                    size="sm"
                    onClick={() => removeAttachment(index)}
                    className="text-synrgy-muted hover:text-red-400 -m-1"
                  >
                    <X className="w-3 h-3" />
                  </TouchButton>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input Container */}
      <div className="relative">
        {/* Syntax Highlighting Overlay */}
        {renderHighlightedInput()}

        {/* Main Textarea */}
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className={`
            w-full resize-none rounded-2xl px-4 py-3 pr-20
            bg-synrgy-bg-950 border border-synrgy-primary/20
            text-synrgy-text placeholder:text-synrgy-muted
            focus:outline-none focus:ring-2 focus:ring-synrgy-primary focus:border-transparent
            ${isMobile ? 'min-h-[48px]' : 'min-h-[44px]'}
            max-h-40 overflow-y-auto transition-all duration-200
          `}
        />

        {/* Character Counter */}
        {inputValue.length > maxLength * 0.8 && (
          <div className={`
            absolute bottom-2 left-4 text-xs
            ${inputValue.length > maxLength * 0.9 ? 'text-red-400' : 'text-synrgy-muted'}
          `}>
            {inputValue.length}/{maxLength}
          </div>
        )}

        {/* Input Actions */}
        <div className="absolute right-2 top-2 flex items-center gap-1">
          {/* Attachment Button */}
          <Tooltip content="Attach files">
            <TouchButton
              variant="ghost"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              className="text-synrgy-muted hover:text-synrgy-primary"
            >
              <Paperclip className="w-4 h-4" />
            </TouchButton>
          </Tooltip>

          {/* Voice Input Button */}
          <Tooltip content={isRecording ? "Stop recording" : "Voice input"}>
            <TouchButton
              variant="ghost"
              size="sm"
              onClick={toggleRecording}
              className={`${
                isRecording ? 'text-red-500 animate-pulse' : 'text-synrgy-muted hover:text-synrgy-primary'
              }`}
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </TouchButton>
          </Tooltip>

          {/* Send Button */}
          <TouchButton
            variant="primary"
            size="sm"
            onClick={handleSend}
            disabled={disabled || (!inputValue.trim() && attachments.length === 0)}
            className="ml-1"
          >
            {disabled ? (
              <LoadingSpinner size="sm" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </TouchButton>
        </div>

        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={handleFileChange}
          accept=".txt,.csv,.json,.log,.pcap,.pdf,.xlsx"
        />
      </div>

      {/* Command Help */}
      <AnimatePresence>
        {commandTokens.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-2 p-2 bg-synrgy-primary/5 rounded-lg border border-synrgy-primary/10"
          >
            <div className="flex items-center gap-2 text-xs text-synrgy-muted">
              <Command className="w-3 h-3" />
              <span>Smart parsing enabled - using</span>
              <div className="flex gap-1">
                {commandTokens.map((token, index) => (
                  <span
                    key={index}
                    className={`
                      px-2 py-0.5 rounded text-xs
                      ${token.type === 'command' && token.valid ? 'bg-blue-100 text-blue-800' : ''}
                      ${token.type === 'parameter' ? 'bg-green-100 text-green-800' : ''}
                      ${token.type === 'value' && token.valid ? 'bg-purple-100 text-purple-800' : ''}
                      ${token.type === 'operator' ? 'bg-orange-100 text-orange-800' : ''}
                      ${!token.valid ? 'bg-red-100 text-red-800' : ''}
                    `}
                  >
                    {token.value}
                  </span>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default EnhancedChatInput
