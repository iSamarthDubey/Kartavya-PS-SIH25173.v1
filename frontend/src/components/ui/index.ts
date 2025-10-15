/**
 * SYNRGY UI Component Library
 * Production-ready, accessible, responsive components with advanced animations
 */

// Loading States & Skeleton Components
export {
  Skeleton,
  ChartSkeleton,
  TableSkeleton,
  CardSkeleton,
  DashboardSkeleton,
  ChatMessageSkeleton,
  LoadingSpinner,
  PageLoadingScreen
} from './Skeleton'

// Advanced Animations & Micro-interactions
export {
  pageVariants,
  slideVariants,
  cardVariants,
  buttonVariants,
  modalVariants,
  listVariants,
  listItemVariants,
  AnimatedPage,
  AnimatedCard,
  AnimatedButton,
  AnimatedList,
  AnimatedListItem,
  AnimatedModal,
  StaggeredGrid,
  FloatingButton,
  PageTransition,
  Spotlight
} from './Animations'

// Accessibility Components
export {
  useA11y,
  A11yProvider,
  ScreenReaderAnnouncer,
  ScreenReaderAssertive,
  SkipLinks,
  AccessibleButton,
  AccessibleInput,
  AccessibleModal,
  AccessibleProgress,
  AccessibleTooltip,
  useKeyboardNavigation
} from './Accessibility'

// Error Handling & User Feedback
export {
  useToast,
  ToastProvider,
  ErrorBoundary,
  EmptyState,
  LoadingState,
  NetworkStatus,
  Retry,
  HelpTooltip,
  QuickActions
} from './Feedback'

// Visual Polish & Theming
export {
  designTokens,
  Glass,
  GradientBackground,
  AnimatedBorder,
  EnhancedCard,
  NeonText,
  ParticleBackground,
  EnhancedButton,
  FloatingElement,
  AnimatedGrid,
  Holographic,
  EnhancedProgressRing
} from './VisualPolish'

// Responsive Design
export {
  breakpoints,
  useBreakpoint,
  ResponsiveContainer,
  ResponsiveGrid,
  MobileDrawer,
  TouchButton,
  ResponsiveModal,
  ResponsiveTabs,
  ResponsiveCardStack,
  ResponsiveText,
  TouchInput,
  spacing,
  ResponsiveSpace
} from './Responsive'
