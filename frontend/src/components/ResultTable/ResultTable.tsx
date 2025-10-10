/**
 * KARTAVYA SIEM - ResultTable Component
 * Paginated table with columns, sorting, and row actions per blueprint
 */

import React, { useState, useMemo } from 'react';
import { 
  ChevronDown, 
  ChevronUp, 
  MoreHorizontal, 
  Download, 
  Search, 
  Shield, 
  Ban, 
  Eye,
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  width?: string;
  render?: (value: any, row: any) => React.ReactNode;
}

interface ResultTableProps {
  data: any[];
  columns?: TableColumn[];
  onRowAction?: (action: string, row: any) => void;
  pageSize?: number;
  title?: string;
}

const ResultTable: React.FC<ResultTableProps> = ({ 
  data = [], 
  columns, 
  onRowAction,
  pageSize = 10,
  title = "Query Results"
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortField, setSortField] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
  const [showColumnSelector, setShowColumnSelector] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Default columns if none provided
  const defaultColumns: TableColumn[] = useMemo(() => {
    if (data.length === 0) return [];
    
    const firstRow = data[0];
    return Object.keys(firstRow).slice(0, 6).map(key => ({
      key,
      label: key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' '),
      sortable: true,
      render: (value, row) => {
        if (key === '@timestamp' || key === 'timestamp') {
          return <span className="font-mono text-xs">{new Date(value).toLocaleString()}</span>;
        }
        if (key === 'src_ip' || key === 'dest_ip' || key.includes('ip')) {
          return <span className="font-mono text-orange-300">{value}</span>;
        }
        if (key === 'user' || key === 'username') {
          return <span className="text-blue-300">{value}</span>;
        }
        if (key === 'severity' || key === 'level') {
          const color = value === 'high' ? 'text-red-300' : value === 'medium' ? 'text-yellow-300' : 'text-green-300';
          return <span className={`${color} capitalize`}>{value}</span>;
        }
        return <span className="text-gray-300">{String(value)}</span>;
      }
    }));
  }, [data]);

  const tableColumns = columns || defaultColumns;

  // Initialize selected columns
  React.useEffect(() => {
    if (selectedColumns.length === 0 && tableColumns.length > 0) {
      setSelectedColumns(tableColumns.map(col => col.key));
    }
  }, [tableColumns, selectedColumns.length]);

  // Filter and sort data
  const processedData = useMemo(() => {
    let filtered = data;
    
    // Search filter
    if (searchTerm) {
      filtered = data.filter(row => 
        Object.values(row).some(value => 
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Sort
    if (sortField) {
      filtered = [...filtered].sort((a, b) => {
        const aVal = a[sortField];
        const bVal = b[sortField];
        
        if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return filtered;
  }, [data, searchTerm, sortField, sortDirection]);

  // Pagination
  const totalPages = Math.ceil(processedData.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedData = processedData.slice(startIndex, startIndex + pageSize);

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleRowAction = (action: string, row: any) => {
    onRowAction?.(action, row);
  };

  const visibleColumns = tableColumns.filter(col => selectedColumns.includes(col.key));

  if (data.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
        <Search className="w-12 h-12 text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-400 mb-2">No Results</h3>
        <p className="text-sm text-gray-500">No data matches your current query</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div>
          <h3 className="text-sm font-semibold text-gray-200">{title}</h3>
          <p className="text-xs text-gray-500">
            {processedData.length} results {searchTerm && `(filtered from ${data.length})`}
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Search */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-2 top-2 text-gray-400" />
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs bg-gray-700 border border-gray-600 rounded focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Column Selector */}
          <div className="relative">
            <button
              onClick={() => setShowColumnSelector(!showColumnSelector)}
              className="p-1.5 bg-gray-700 hover:bg-gray-600 border border-gray-600 rounded transition-colors"
              title="Configure columns"
            >
              <Settings className="w-4 h-4 text-gray-400" />
            </button>
            
            {showColumnSelector && (
              <div className="absolute right-0 top-full mt-2 bg-gray-800 border border-gray-600 rounded-lg shadow-lg z-10 min-w-48">
                <div className="p-3">
                  <h4 className="text-xs font-semibold text-gray-400 mb-2">Columns</h4>
                  {tableColumns.map(col => (
                    <label key={col.key} className="flex items-center space-x-2 py-1">
                      <input
                        type="checkbox"
                        checked={selectedColumns.includes(col.key)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedColumns([...selectedColumns, col.key]);
                          } else {
                            setSelectedColumns(selectedColumns.filter(k => k !== col.key));
                          }
                        }}
                        className="w-3 h-3"
                      />
                      <span className="text-xs text-gray-300">{col.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Export */}
          <button
            onClick={() => handleRowAction('export-all', processedData)}
            className="p-1.5 bg-gray-700 hover:bg-gray-600 border border-gray-600 rounded transition-colors"
            title="Export results"
          >
            <Download className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-900/50">
            <tr>
              {visibleColumns.map(col => (
                <th
                  key={col.key}
                  className={`text-left p-3 text-xs font-semibold text-gray-400 ${
                    col.sortable ? 'cursor-pointer hover:text-gray-300' : ''
                  }`}
                  style={{ width: col.width }}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className="flex items-center space-x-1">
                    <span>{col.label}</span>
                    {col.sortable && sortField === col.key && (
                      sortDirection === 'asc' ? 
                        <ChevronUp className="w-3 h-3" /> : 
                        <ChevronDown className="w-3 h-3" />
                    )}
                  </div>
                </th>
              ))}
              <th className="w-12 p-3"></th> {/* Actions column */}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, index) => (
              <tr key={index} className="border-t border-gray-700 hover:bg-gray-900/30 transition-colors">
                {visibleColumns.map(col => (
                  <td key={col.key} className="p-3 text-xs">
                    {col.render ? col.render(row[col.key], row) : String(row[col.key] || '')}
                  </td>
                ))}
                
                {/* Row Actions */}
                <td className="p-3">
                  <div className="relative group">
                    <button className="p-1 hover:bg-gray-700 rounded transition-colors">
                      <MoreHorizontal className="w-4 h-4 text-gray-400" />
                    </button>
                    
                    {/* Action Menu */}
                    <div className="absolute right-0 top-full mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity z-10 min-w-32">
                      <div className="py-1">
                        <button
                          onClick={() => handleRowAction('investigate', row)}
                          className="flex items-center space-x-2 w-full px-3 py-1.5 text-xs text-left hover:bg-gray-700 transition-colors"
                        >
                          <Search className="w-3 h-3" />
                          <span>Investigate</span>
                        </button>
                        <button
                          onClick={() => handleRowAction('view-details', row)}
                          className="flex items-center space-x-2 w-full px-3 py-1.5 text-xs text-left hover:bg-gray-700 transition-colors"
                        >
                          <Eye className="w-3 h-3" />
                          <span>View Details</span>
                        </button>
                        {(row.src_ip || row.ip) && (
                          <button
                            onClick={() => handleRowAction('block-ip', row)}
                            className="flex items-center space-x-2 w-full px-3 py-1.5 text-xs text-left hover:bg-gray-700 text-red-300 transition-colors"
                          >
                            <Ban className="w-3 h-3" />
                            <span>Block IP</span>
                          </button>
                        )}
                        <button
                          onClick={() => handleRowAction('create-rule', row)}
                          className="flex items-center space-x-2 w-full px-3 py-1.5 text-xs text-left hover:bg-gray-700 transition-colors"
                        >
                          <Shield className="w-3 h-3" />
                          <span>Create Rule</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between p-4 border-t border-gray-700">
          <div className="text-xs text-gray-500">
            Showing {startIndex + 1}-{Math.min(startIndex + pageSize, processedData.length)} of {processedData.length}
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="p-1 hover:bg-gray-700 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4 text-gray-400" />
            </button>
            
            <span className="text-xs text-gray-400">
              {currentPage} / {totalPages}
            </span>
            
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="p-1 hover:bg-gray-700 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultTable;
