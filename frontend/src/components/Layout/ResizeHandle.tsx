/**
 * KARTAVYA SIEM - Resize Handle Component
 * Provides drag handles for resizable panels
 */

import React, { useCallback, useEffect, useState } from 'react';
import { useLayout } from '../../contexts/LayoutContext';

interface ResizeHandleProps {
  direction: 'vertical' | 'horizontal';
  onResize: (delta: number) => void;
  className?: string;
}

const ResizeHandle: React.FC<ResizeHandleProps> = ({ 
  direction, 
  onResize, 
  className = '' 
}) => {
  const { actions } = useLayout();
  const [isDragging, setIsDragging] = useState(false);
  const [startPosition, setStartPosition] = useState({ x: 0, y: 0 });

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    setStartPosition({ x: e.clientX, y: e.clientY });
    actions.setIsResizing(true);
    actions.setLastInteraction('panels');
    
    // Add cursor style to body
    document.body.style.cursor = direction === 'vertical' ? 'col-resize' : 'row-resize';
    document.body.style.userSelect = 'none';
  }, [direction, actions]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging) return;

    const delta = direction === 'vertical' 
      ? e.clientX - startPosition.x 
      : e.clientY - startPosition.y;

    onResize(delta);
    setStartPosition({ x: e.clientX, y: e.clientY });
  }, [isDragging, direction, startPosition, onResize]);

  const handleMouseUp = useCallback(() => {
    if (!isDragging) return;

    setIsDragging(false);
    actions.setIsResizing(false);
    
    // Reset cursor style
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }, [isDragging, actions]);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const baseClasses = direction === 'vertical'
    ? 'w-1 cursor-col-resize hover:bg-blue-500/30 active:bg-blue-500/50'
    : 'h-1 cursor-row-resize hover:bg-blue-500/30 active:bg-blue-500/50';

  const draggingClasses = isDragging
    ? 'bg-blue-500/50 resize-handle-active'
    : 'bg-transparent hover:bg-gray-600/50';

  return (
    <div
      className={`
        ${baseClasses} 
        ${draggingClasses} 
        transition-colors duration-150 
        flex-shrink-0 
        ${className}
        ${isDragging ? 'panel-resizing' : ''}
      `}
      onMouseDown={handleMouseDown}
      role="separator"
      aria-label={`Resize ${direction === 'vertical' ? 'width' : 'height'}`}
    >
      {/* Visual indicator */}
      <div className={`
        ${direction === 'vertical' ? 'w-full h-8 mx-auto' : 'h-full w-8 my-auto'}
        ${direction === 'vertical' ? 'border-l-2' : 'border-t-2'}
        border-gray-600/50 hover:border-blue-500/50 transition-colors
        ${isDragging ? 'border-blue-500' : ''}
      `} />
    </div>
  );
};

export default ResizeHandle;
