# SYNRGY UI Component Library

A comprehensive, production-ready UI component library built for the SYNRGY SIEM platform. Features advanced animations, accessibility support, responsive design, and sophisticated visual effects.

## 🚀 Features

- **🎭 Advanced Animations**: Smooth transitions using Framer Motion
- ♿ **Accessibility First**: WCAG 2.1 AA compliant with screen reader support
- 📱 **Responsive Design**: Mobile-first approach with touch optimizations
- 🎨 **Visual Polish**: Modern design system with glassmorphism, gradients, and effects
- 🔄 **Smart Loading States**: Skeleton screens and performance-optimized loading
- 🛠️ **Error Handling**: Comprehensive error boundaries and user feedback
- ⚡ **Performance**: Virtualization and optimizations for large datasets

## 📦 Component Categories

### 1. Loading States & Skeleton Components

Perfect perceived performance with sophisticated loading states:

```typescript
import { DashboardSkeleton, LoadingSpinner, PageLoadingScreen } from '@/components/UI'

// Dashboard loading state
<DashboardSkeleton />

// Custom loading spinner
<LoadingSpinner size="lg" />

// Full page loading
<PageLoadingScreen message="Loading SYNRGY..." />
```

### 2. Advanced Animations & Micro-interactions

Smooth, delightful animations throughout the interface:

```typescript
import { AnimatedPage, AnimatedCard, StaggeredGrid, Spotlight } from '@/components/UI'

// Page transitions
<AnimatedPage>
  <YourPageContent />
</AnimatedPage>

// Interactive cards
<AnimatedCard hoverable onClick={() => console.log('clicked')}>
  <CardContent />
</AnimatedCard>

// Staggered grid animations
<StaggeredGrid staggerDelay={0.1}>
  {items.map(item => <Item key={item.id} />)}
</StaggeredGrid>

// Spotlight effects for important elements
<Spotlight intensity="high" color="primary">
  <ImportantContent />
</Spotlight>
```

### 3. Accessibility Components

Full accessibility support with screen reader integration:

```typescript
import { 
  A11yProvider, 
  AccessibleButton, 
  AccessibleModal,
  useA11y 
} from '@/components/UI'

// Wrap your app
<A11yProvider>
  <YourApp />
</A11yProvider>

// Accessible button with keyboard shortcuts
<AccessibleButton
  shortcut="Enter"
  description="Save your changes"
  onClick={handleSave}
>
  Save
</AccessibleButton>

// Screen reader announcements
const { announceToScreenReader } = useA11y()
announceToScreenReader('Data updated successfully', 'assertive')
```

### 4. Error Handling & User Feedback

Beautiful error states and user feedback:

```typescript
import { 
  ToastProvider, 
  useToast, 
  ErrorBoundary, 
  EmptyState,
  NetworkStatus 
} from '@/components/UI'

// Toast notifications
const { showToast } = useToast()
showToast({
  type: 'success',
  title: 'Success!',
  message: 'Data saved successfully',
  action: { label: 'View', onClick: handleView }
})

// Error boundaries
<ErrorBoundary fallback={CustomErrorComponent}>
  <YourComponent />
</ErrorBoundary>

// Empty states
<EmptyState
  title="No data found"
  description="Try adjusting your filters"
  action={{ label: 'Reset Filters', onClick: handleReset }}
/>

// Network status indicator
<NetworkStatus />
```

### 5. Visual Polish & Theming

Modern visual effects and theming:

```typescript
import { 
  Glass, 
  GradientBackground, 
  EnhancedCard,
  NeonText,
  Holographic,
  designTokens 
} from '@/components/UI'

// Glassmorphism effects
<Glass intensity="medium">
  <Content />
</Glass>

// Gradient backgrounds
<GradientBackground variant="brand" animated>
  <HeroContent />
</GradientBackground>

// Enhanced cards with visual effects
<EnhancedCard variant="glow" hoverable>
  <CardContent />
</EnhancedCard>

// Neon text effects
<NeonText intensity="strong" color="#00EFFF">
  ＳＹＮＲＧＹ
</NeonText>

// Access design tokens
const { gradients, shadows, spacing } = designTokens
```

### 6. Responsive Design

Mobile-first, touch-optimized components:

```typescript
import { 
  ResponsiveContainer, 
  ResponsiveGrid,
  TouchButton,
  ResponsiveModal,
  useBreakpoint 
} from '@/components/UI'

// Responsive container
<ResponsiveContainer maxWidth="xl" padding>
  <Content />
</ResponsiveContainer>

// Responsive grid
<ResponsiveGrid 
  columns={{ sm: 1, md: 2, lg: 3, xl: 4 }}
  gap={6}
>
  {items.map(item => <Card key={item.id} />)}
</ResponsiveGrid>

// Touch-optimized buttons
<TouchButton variant="primary" size="lg" fullWidth>
  Touch-Friendly Action
</TouchButton>

// Responsive hook
const { isMobile, isTablet, isDesktop } = useBreakpoint()
```

## 🎨 Design System

### Color Palette
- **Primary**: `#00EFFF` (Cyan)
- **Accent**: `#FF7A00` (Orange)
- **Surface**: Dark theme optimized
- **Text**: High contrast for accessibility

### Typography
- **Headings**: Font weights 600-800
- **Body**: Font weight 400-500
- **Code**: Monospace for data display

### Spacing Scale
- **xs**: 4px
- **sm**: 8px
- **md**: 16px
- **lg**: 24px
- **xl**: 32px
- **2xl**: 48px
- **3xl**: 64px

### Breakpoints
- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px
- **2xl**: 1536px

## 📱 Mobile Optimization

All components are optimized for mobile devices:

- **Touch Targets**: Minimum 44px touch targets
- **Gestures**: Swipe, pinch, tap optimizations
- **Performance**: Virtualized lists and lazy loading
- **Accessibility**: Voice control and screen reader support

## ⚡ Performance Features

- **Virtualization**: Handle thousands of items efficiently
- **Lazy Loading**: Components load on demand
- **Memoization**: React.memo and useMemo optimizations
- **Bundle Splitting**: Tree-shakeable imports

## 🧪 Usage Examples

### Dashboard with Loading States
```typescript
import { DashboardSkeleton, ResponsiveGrid, EnhancedCard } from '@/components/UI'

function Dashboard() {
  const { data, loading } = useData()
  
  if (loading) return <DashboardSkeleton />
  
  return (
    <ResponsiveGrid columns={{ sm: 1, lg: 3 }}>
      {data.map(item => (
        <EnhancedCard key={item.id} variant="glass" hoverable>
          {item.content}
        </EnhancedCard>
      ))}
    </ResponsiveGrid>
  )
}
```

### Error Handling
```typescript
import { ErrorBoundary, ToastProvider } from '@/components/UI'

function App() {
  return (
    <ToastProvider position="top-right">
      <ErrorBoundary>
        <YourApp />
      </ErrorBoundary>
    </ToastProvider>
  )
}
```

### Responsive Chat Interface
```typescript
import { ResponsiveModal, TouchButton, ChatMessageSkeleton } from '@/components/UI'

function ChatInterface() {
  const { isMobile } = useBreakpoint()
  
  return (
    <ResponsiveModal
      isOpen={isOpen}
      onClose={onClose}
      title="SYNRGY Assistant"
      size={isMobile ? 'full' : 'lg'}
    >
      {loading ? (
        <ChatMessageSkeleton />
      ) : (
        <ChatContent />
      )}
      
      <TouchButton variant="primary" fullWidth>
        Send Message
      </TouchButton>
    </ResponsiveModal>
  )
}
```

## 🔧 Customization

Components support extensive customization through props and CSS custom properties:

```typescript
// Custom theme colors
<EnhancedButton
  variant="gradient"
  style={{ 
    '--primary-color': '#your-color',
    '--accent-color': '#your-accent'
  }}
>
  Custom Button
</EnhancedButton>

// Custom animations
<AnimatedCard
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.5 }}
>
  Custom Animation
</AnimatedCard>
```

## 📈 Performance Monitoring

Built-in performance monitoring for production optimization:

```typescript
import { performanceMonitor } from '@/services/performance'

// Components automatically track render times
// Access performance data in development mode
console.log(performanceMonitor.getMetrics())
```

## 🧩 Integration

Easy integration with existing SYNRGY components:

```typescript
// Use alongside existing components
import { VisualRenderer } from '@/components/Visuals'
import { EnhancedCard, LoadingState } from '@/components/UI'

<EnhancedCard variant="glass">
  {loading ? (
    <LoadingState />
  ) : (
    <VisualRenderer payload={data} />
  )}
</EnhancedCard>
```

## 🎯 Best Practices

1. **Always wrap your app with providers**:
   ```typescript
   <A11yProvider>
     <ToastProvider>
       <App />
     </ToastProvider>
   </A11yProvider>
   ```

2. **Use semantic components for better accessibility**:
   ```typescript
   <AccessibleButton description="Save document">
     Save
   </AccessibleButton>
   ```

3. **Implement proper loading states**:
   ```typescript
   {loading ? <TableSkeleton /> : <DataTable />}
   ```

4. **Optimize for mobile**:
   ```typescript
   const { isMobile } = useBreakpoint()
   return isMobile ? <MobileView /> : <DesktopView />
   ```

5. **Handle errors gracefully**:
   ```typescript
   <ErrorBoundary fallback={CustomErrorFallback}>
     <Component />
   </ErrorBoundary>
   ```

## 🚀 Production Ready

All components are production-ready with:

- ✅ TypeScript support
- ✅ Unit tests
- ✅ Accessibility compliance
- ✅ Mobile optimization
- ✅ Performance optimization
- ✅ Error handling
- ✅ Documentation

---

**Built with ❤️ for the SYNRGY SIEM Platform**
