/**
 * SYNRGY TableRenderer
 * Interactive security data tables with sorting, filtering, and pagination
 * Handles IP addresses, timestamps, threat data, and more
 */

import React, { useState, useMemo } from 'react'
import { 
  ChevronUp, ChevronDown, ChevronsUpDown, 
  Search, Filter, Eye, EyeOff, 
  ArrowLeft, ArrowRight 
} from 'lucide-react'
import type { VisualCard, TableCard } from '@/types'

interface TableRendererProps {
  card: VisualCard
  compact?: boolean
  onError?: (error: any) => void
}

/**
 * Column type formatting and styling
 */
const COLUMN_TYPES = {
  ip: {
    format: (value: string) => value,
    className: 'font-mono text-synrgy-primary',
    sortType: 'string'
  },
  url: {
    format: (value: string) => value.length > 40 ? `${value.substring(0, 40)}...` : value,
    className: 'font-mono text-blue-400 truncate',
    sortType: 'string'
  },
  date: {
    format: (value: string | number) => {
      const date = new Date(value)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    className: 'text-synrgy-muted',
    sortType: 'date'
  },
  number: {
    format: (value: number) => {
      if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`
      if (value >= 1000) return `${(value / 1000).toFixed(1)}K`
      return value.toLocaleString()
    },
    className: 'text-right font-mono text-synrgy-accent',
    sortType: 'number'
  },
  string: {
    format: (value: string) => value,
    className: 'text-synrgy-text',
    sortType: 'string'
  }
}

/**
 * Sort function for different data types
 */
const sortData = (data: any[][], columnIndex: number, direction: 'asc' | 'desc', sortType: string) => {
  return [...data].sort((a, b) => {
    const aVal = a[columnIndex]
    const bVal = b[columnIndex]
    
    let comparison = 0
    
    switch (sortType) {
      case 'number':
        comparison = (aVal || 0) - (bVal || 0)
        break
      case 'date':
        comparison = new Date(aVal || 0).getTime() - new Date(bVal || 0).getTime()
        break
      default:
        comparison = String(aVal || '').localeCompare(String(bVal || ''))
    }
    
    return direction === 'asc' ? comparison : -comparison
  })
}

/**
 * Filter function for table data
 */
const filterData = (data: any[][], columns: any[], searchTerm: string) => {
  if (!searchTerm.trim()) return data
  
  const term = searchTerm.toLowerCase()
  return data.filter(row =>
    row.some((cell, index) => {
      const column = columns[index]
      const value = String(cell || '').toLowerCase()
      
      // Special handling for IP addresses
      if (column?.type === 'ip') {
        return value.includes(term)
      }
      
      return value.includes(term)
    })
  )
}

/**
 * Table header with sorting
 */
const TableHeader: React.FC<{
  columns: any[]
  sortBy?: { column: number, direction: 'asc' | 'desc' }
  onSort: (columnIndex: number) => void
  compact: boolean
}> = ({ columns, sortBy, onSort, compact }) => (
  <thead className="bg-synrgy-surface/30">
    <tr>
      {columns.map((column, index) => {
        const isSorted = sortBy?.column === index
        const sortDirection = isSorted ? sortBy.direction : null
        
        return (
          <th
            key={index}
            className={`
              px-3 py-2 text-left border-b border-synrgy-primary/10
              ${column.sortable !== false ? 'cursor-pointer hover:bg-synrgy-primary/5' : ''}
              ${compact ? 'text-xs' : 'text-sm'}
            `}
            onClick={() => column.sortable !== false && onSort(index)}
            style={{ width: column.width || 'auto' }}
          >
            <div className="flex items-center gap-2">
              <span className="font-medium text-synrgy-text truncate">
                {column.label}
              </span>
              {column.sortable !== false && (
                <div className="flex flex-col">
                  {sortDirection === 'asc' ? (
                    <ChevronUp className="w-3 h-3 text-synrgy-primary" />
                  ) : sortDirection === 'desc' ? (
                    <ChevronDown className="w-3 h-3 text-synrgy-primary" />
                  ) : (
                    <ChevronsUpDown className="w-3 h-3 text-synrgy-muted" />
                  )}
                </div>
              )}
            </div>
          </th>
        )
      })}
    </tr>
  </thead>
)

/**
 * Table row component
 */
const TableRow: React.FC<{
  row: any[]
  columns: any[]
  index: number
  compact: boolean
}> = ({ row, columns, index, compact }) => (
  <tr className={`
    border-b border-synrgy-primary/5 hover:bg-synrgy-primary/5
    ${index % 2 === 0 ? 'bg-synrgy-surface/20' : 'bg-transparent'}
  `}>
    {row.map((cell, cellIndex) => {
      const column = columns[cellIndex]
      const columnType = COLUMN_TYPES[column?.type || 'string']
      const formattedValue = columnType.format(cell)
      
      return (
        <td
          key={cellIndex}
          className={`
            px-3 py-2 ${columnType.className}
            ${compact ? 'text-xs' : 'text-sm'}
          `}
          title={String(cell)} // Full value on hover
        >
          {formattedValue}
        </td>
      )
    })}
  </tr>
)

/**
 * Pagination component
 */
const Pagination: React.FC<{
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  totalItems: number
  itemsPerPage: number
}> = ({ currentPage, totalPages, onPageChange, totalItems, itemsPerPage }) => {
  const startItem = (currentPage - 1) * itemsPerPage + 1
  const endItem = Math.min(currentPage * itemsPerPage, totalItems)
  
  return (
    <div className="flex items-center justify-between mt-4 pt-3 border-t border-synrgy-primary/10">
      <div className="text-xs text-synrgy-muted">
        Showing {startItem}-{endItem} of {totalItems} results
      </div>
      
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          className="p-1 rounded hover:bg-synrgy-primary/10 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ArrowLeft className="w-4 h-4 text-synrgy-muted" />
        </button>
        
        <span className="text-sm text-synrgy-text px-2">
          {currentPage} / {totalPages}
        </span>
        
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="p-1 rounded hover:bg-synrgy-primary/10 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ArrowRight className="w-4 h-4 text-synrgy-muted" />
        </button>
      </div>
    </div>
  )
}

/**
 * Main TableRenderer component
 */
const TableRenderer: React.FC<TableRendererProps> = ({
  card,
  compact = false,
  onError
}) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState<{ column: number, direction: 'asc' | 'desc' } | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  
  try {
    const tableCard = card as TableCard
    
    // Validate data
    if (!tableCard.columns || !tableCard.rows || tableCard.rows.length === 0) {
      return (
        <div className="p-6 bg-synrgy-surface/50 rounded-lg border border-synrgy-primary/10 text-center">
          <Filter className="w-8 h-8 text-synrgy-muted mx-auto mb-2" />
          <p className="text-synrgy-muted text-sm">No table data available</p>
        </div>
      )
    }
    
    // Process data
    const filteredData = useMemo(() => 
      filterData(tableCard.rows, tableCard.columns, searchTerm),
      [tableCard.rows, tableCard.columns, searchTerm]
    )
    
    const sortedData = useMemo(() => {
      if (!sortBy) return filteredData
      
      const column = tableCard.columns[sortBy.column]
      const sortType = COLUMN_TYPES[column?.type || 'string'].sortType
      
      return sortData(filteredData, sortBy.column, sortBy.direction, sortType)
    }, [filteredData, sortBy, tableCard.columns])
    
    // Pagination
    const itemsPerPage = compact ? 5 : 10
    const totalPages = Math.ceil(sortedData.length / itemsPerPage)
    const startIndex = (currentPage - 1) * itemsPerPage
    const paginatedData = sortedData.slice(startIndex, startIndex + itemsPerPage)
    
    // Handle sorting
    const handleSort = (columnIndex: number) => {
      setSortBy(prev => {
        if (prev?.column === columnIndex) {
          return prev.direction === 'asc' 
            ? { column: columnIndex, direction: 'desc' }
            : null
        }
        return { column: columnIndex, direction: 'asc' }
      })
      setCurrentPage(1) // Reset to first page when sorting
    }
    
    return (
      <div className="bg-synrgy-surface/50 rounded-lg border border-synrgy-primary/10">
        {/* Table Header */}
        <div className="p-4 border-b border-synrgy-primary/10">
          <div className="flex items-center justify-between">
            <div>
              <h3 className={`font-medium text-synrgy-text ${compact ? 'text-sm' : 'text-base'}`}>
                {tableCard.title || 'Security Data'}
              </h3>
              {tableCard.subtitle && !compact && (
                <p className="text-xs text-synrgy-muted mt-0.5">
                  {tableCard.subtitle}
                </p>
              )}
            </div>
            
            {/* Search */}
            {!compact && (
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-synrgy-muted" />
                <input
                  type="text"
                  placeholder="Search data..."
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value)
                    setCurrentPage(1) // Reset to first page when searching
                  }}
                  className="pl-10 pr-4 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg text-sm text-synrgy-text focus:outline-none focus:border-synrgy-primary/50"
                />
              </div>
            )}
          </div>
        </div>
        
        {/* Table Content */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <TableHeader
              columns={tableCard.columns}
              sortBy={sortBy}
              onSort={handleSort}
              compact={compact}
            />
            <tbody>
              {paginatedData.map((row, index) => (
                <TableRow
                  key={startIndex + index}
                  row={row}
                  columns={tableCard.columns}
                  index={index}
                  compact={compact}
                />
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-4 pb-4">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              totalItems={sortedData.length}
              itemsPerPage={itemsPerPage}
            />
          </div>
        )}
        
        {/* Empty State */}
        {paginatedData.length === 0 && searchTerm && (
          <div className="p-8 text-center">
            <Search className="w-8 h-8 text-synrgy-muted mx-auto mb-2" />
            <p className="text-synrgy-muted text-sm">
              No results found for "{searchTerm}"
            </p>
            <button
              onClick={() => setSearchTerm('')}
              className="mt-2 text-xs text-synrgy-primary hover:underline"
            >
              Clear search
            </button>
          </div>
        )}
      </div>
    )
  } catch (error) {
    onError?.(error)
    return (
      <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
        <div className="text-red-400 text-sm">
          Failed to render table: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      </div>
    )
  }
}

export default TableRenderer
