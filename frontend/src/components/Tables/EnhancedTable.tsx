import React, { memo, useState, useCallback, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Paper,
  Checkbox,
  IconButton,
  TextField,
  InputAdornment,
  Chip,
  Box,
  Typography,
  useTheme,
  alpha,
  Skeleton,
  Collapse,
  Tooltip,
  Menu,
  MenuItem,
  useMediaQuery,
} from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';
import {
  Search as SearchIcon,
  MoreVert as MoreVertIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';

// Enhanced animations
const tableAnimations = {
  slideIn: keyframes`
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  `,
  
  highlight: keyframes`
    0% { background-color: transparent; }
    50% { background-color: rgba(25, 118, 210, 0.1); }
    100% { background-color: transparent; }
  `,
  
  shimmer: keyframes`
    0% { background-position: -200px 0; }
    100% { background-position: calc(200px + 100%) 0; }
  `,
};

// Enhanced Table Container
const StyledTableContainer = styled(TableContainer)(({ theme }) => ({
  borderRadius: theme.spacing(2),
  overflow: 'hidden',
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  boxShadow: `0 4px 20px ${alpha(theme.palette.common.black, 0.05)}`,
  
  '& .MuiTable-root': {
    minWidth: 650,
  },
}));

// Enhanced Table Header
const StyledTableHead = styled(TableHead)(({ theme }) => ({
  background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.primary.main, 0.02)} 100%)`,
  
  '& .MuiTableCell-head': {
    fontWeight: 700,
    fontSize: '0.875rem',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    color: theme.palette.text.primary,
    borderBottom: `2px solid ${alpha(theme.palette.primary.main, 0.1)}`,
    padding: theme.spacing(2),
    
    '&:first-of-type': {
      paddingLeft: theme.spacing(3),
    },
    
    '&:last-of-type': {
      paddingRight: theme.spacing(3),
    },
  },
}));

// Enhanced Table Row
const StyledTableRow = styled(TableRow, {
  shouldForwardProp: (prop) => !['isSelected', 'isClickable'].includes(prop as string),
})<{ isSelected?: boolean; isClickable?: boolean }>(({ theme, isSelected, isClickable }) => ({
  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
  
  ...(isClickable && {
    cursor: 'pointer',
    
    '&:hover': {
      backgroundColor: alpha(theme.palette.primary.main, 0.04),
      transform: 'translateY(-1px)',
      boxShadow: `0 4px 12px ${alpha(theme.palette.common.black, 0.1)}`,
    },
  }),
  
  ...(isSelected && {
    backgroundColor: alpha(theme.palette.primary.main, 0.08),
    
    '&:hover': {
      backgroundColor: alpha(theme.palette.primary.main, 0.12),
    },
  }),
  
  '& .MuiTableCell-body': {
    borderBottom: `1px solid ${alpha(theme.palette.divider, 0.05)}`,
    padding: theme.spacing(2),
    
    '&:first-of-type': {
      paddingLeft: theme.spacing(3),
    },
    
    '&:last-of-type': {
      paddingRight: theme.spacing(3),
    },
  },
}));

// Table Toolbar
const TableToolbar = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2, 3),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
  backdropFilter: 'blur(20px)',
  
  [theme.breakpoints.down('md')]: {
    flexDirection: 'column',
    gap: theme.spacing(2),
    alignItems: 'stretch',
  },
}));

// Search Field
const SearchField = styled(TextField)(({ theme }) => ({
  minWidth: 300,
  
  '& .MuiOutlinedInput-root': {
    borderRadius: theme.spacing(3),
    backgroundColor: alpha(theme.palette.background.paper, 0.8),
    
    '&:hover': {
      backgroundColor: alpha(theme.palette.background.paper, 0.9),
    },
    
    '&.Mui-focused': {
      backgroundColor: theme.palette.background.paper,
    },
  },
  
  [theme.breakpoints.down('md')]: {
    minWidth: 'unset',
    width: '100%',
  },
}));

// Action Button Group
const ActionButtonGroup = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  
  [theme.breakpoints.down('md')]: {
    justifyContent: 'center',
    flexWrap: 'wrap',
  },
}));

// Column Definition Interface
export interface ColumnDef<T = any> {
  id: string;
  label: string;
  accessor: keyof T | ((row: T) => any);
  sortable?: boolean;
  filterable?: boolean;
  width?: number | string;
  minWidth?: number;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: T, index: number) => React.ReactNode;
  headerRender?: () => React.ReactNode;
}

// Table Props Interface
export interface EnhancedTableProps<T = any> {
  data: T[];
  columns: ColumnDef<T>[];
  loading?: boolean;
  selectable?: boolean;
  selectedRows?: T[];
  onSelectionChange?: (selected: T[]) => void;
  onRowClick?: (row: T, index: number) => void;
  expandable?: boolean;
  renderExpandedRow?: (row: T, index: number) => React.ReactNode;
  searchable?: boolean;
  searchValue?: string;
  onSearchChange?: (value: string) => void;
  sortable?: boolean;
  pagination?: boolean;
  pageSize?: number;
  page?: number;
  totalCount?: number;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  onSortChange?: (column: string, direction: 'asc' | 'desc') => void;
  actions?: Array<{
    label: string;
    icon?: React.ReactNode;
    onClick: () => void;
    disabled?: boolean;
  }>;
  emptyMessage?: string;
  className?: string;
  sx?: object;
}

// Table Skeleton Component
const TableSkeleton = memo<{ columns: number; rows: number }>(({ columns, rows }) => (
  <>
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <StyledTableRow key={rowIndex}>
        {Array.from({ length: columns }).map((_, colIndex) => (
          <TableCell key={colIndex}>
            <Skeleton
              variant="text"
              height={24}
              sx={{
                background: `linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)`,
                backgroundSize: '200px 100%',
                animation: `${tableAnimations.shimmer} 1.5s infinite`,
              }}
            />
          </TableCell>
        ))}
      </StyledTableRow>
    ))}
  </>
));

TableSkeleton.displayName = 'TableSkeleton';

// Enhanced Sort Label
const EnhancedSortLabel = memo<{
  active: boolean;
  direction: 'asc' | 'desc';
  onClick: () => void;
  children: React.ReactNode;
}>(({ active, direction, onClick, children }) => (
  <TableSortLabel
    active={active}
    direction={direction}
    onClick={onClick}
    sx={{
      '& .MuiTableSortLabel-icon': {
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      },
    }}
  >
    {children}
  </TableSortLabel>
));

EnhancedSortLabel.displayName = 'EnhancedSortLabel';

// Main Enhanced Table Component
const EnhancedTable = memo<EnhancedTableProps>(({
  data,
  columns,
  loading = false,
  selectable = false,
  selectedRows = [],
  onSelectionChange,
  onRowClick,
  expandable = false,
  renderExpandedRow,
  searchable = false,
  searchValue = '',
  onSearchChange,
  sortable = true,
  pagination = true,
  pageSize = 10,
  page = 0,
  totalCount,
  onPageChange,
  onPageSizeChange,
  onSortChange,
  actions = [],
  emptyMessage = 'No hay datos disponibles',
  className,
  sx,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [internalSearchValue, setInternalSearchValue] = useState(searchValue);
  const [sortColumn, setSortColumn] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [actionMenuAnchor, setActionMenuAnchor] = useState<null | HTMLElement>(null);
  
  // Handle search
  const handleSearchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setInternalSearchValue(value);
    onSearchChange?.(value);
  }, [onSearchChange]);
  
  // Handle sorting
  const handleSort = useCallback((columnId: string) => {
    const isAsc = sortColumn === columnId && sortDirection === 'asc';
    const newDirection = isAsc ? 'desc' : 'asc';
    
    setSortColumn(columnId);
    setSortDirection(newDirection);
    onSortChange?.(columnId, newDirection);
  }, [sortColumn, sortDirection, onSortChange]);
  
  // Handle row selection
  const handleSelectAll = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      onSelectionChange?.(data);
    } else {
      onSelectionChange?.([]);
    }
  }, [data, onSelectionChange]);
  
  const handleSelectRow = useCallback((row: any) => {
    const isSelected = selectedRows.some(selected => selected === row);
    
    if (isSelected) {
      onSelectionChange?.(selectedRows.filter(selected => selected !== row));
    } else {
      onSelectionChange?.([...selectedRows, row]);
    }
  }, [selectedRows, onSelectionChange]);
  
  // Handle row expansion
  const handleExpandRow = useCallback((index: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedRows(newExpanded);
  }, [expandedRows]);
  
  // Handle action menu
  const handleActionMenuOpen = useCallback((event: React.MouseEvent<HTMLElement>) => {
    setActionMenuAnchor(event.currentTarget);
  }, []);
  
  const handleActionMenuClose = useCallback(() => {
    setActionMenuAnchor(null);
  }, []);
  
  // Memoized filtered and sorted data
  const processedData = useMemo(() => {
    let result = [...data];
    
    // Apply search filter
    if (searchable && (onSearchChange ? searchValue : internalSearchValue)) {
      const searchTerm = (onSearchChange ? searchValue : internalSearchValue).toLowerCase();
      result = result.filter(row =>
        columns.some(column => {
          const value = typeof column.accessor === 'function' 
            ? column.accessor(row) 
            : row[column.accessor];
          return String(value).toLowerCase().includes(searchTerm);
        })
      );
    }
    
    return result;
  }, [data, columns, searchable, searchValue, internalSearchValue, onSearchChange]);
  
  const isAllSelected = selectedRows.length === data.length && data.length > 0;
  const isIndeterminate = selectedRows.length > 0 && selectedRows.length < data.length;
  
  return (
    <Paper className={className} sx={sx}>
      {/* Table Toolbar */}
      {(searchable || actions.length > 0) && (
        <TableToolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
            {searchable && (
              <SearchField
                placeholder="Buscar..."
                value={onSearchChange ? searchValue : internalSearchValue}
                onChange={handleSearchChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                size="small"
              />
            )}
            
            {selectable && selectedRows.length > 0 && (
              <Chip
                label={`${selectedRows.length} seleccionado${selectedRows.length > 1 ? 's' : ''}`}
                color="primary"
                variant="outlined"
                size="small"
              />
            )}
          </Box>
          
          {actions.length > 0 && (
            <ActionButtonGroup>
              {!isMobile ? (
                actions.map((action, index) => (
                  <Tooltip key={index} title={action.label}>
                    <IconButton
                      onClick={action.onClick}
                      disabled={action.disabled}
                      size="small"
                    >
                      {action.icon}
                    </IconButton>
                  </Tooltip>
                ))
              ) : (
                <>
                  <IconButton onClick={handleActionMenuOpen} size="small">
                    <MoreVertIcon />
                  </IconButton>
                  <Menu
                    anchorEl={actionMenuAnchor}
                    open={Boolean(actionMenuAnchor)}
                    onClose={handleActionMenuClose}
                  >
                    {actions.map((action, index) => (
                      <MenuItem
                        key={index}
                        onClick={() => {
                          action.onClick();
                          handleActionMenuClose();
                        }}
                        disabled={action.disabled}
                      >
                        {action.icon && <Box sx={{ mr: 1 }}>{action.icon}</Box>}
                        {action.label}
                      </MenuItem>
                    ))}
                  </Menu>
                </>
              )}
            </ActionButtonGroup>
          )}
        </TableToolbar>
      )}
      
      {/* Table */}
      <StyledTableContainer>
        <Table stickyHeader>
          <StyledTableHead>
            <TableRow>
              {selectable && (
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={isIndeterminate}
                    checked={isAllSelected}
                    onChange={handleSelectAll}
                    color="primary"
                  />
                </TableCell>
              )}
              
              {expandable && <TableCell />}
              
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align || 'left'}
                  style={{
                    width: column.width,
                    minWidth: column.minWidth,
                  }}
                >
                  {column.headerRender ? (
                    column.headerRender()
                  ) : sortable && column.sortable !== false ? (
                    <EnhancedSortLabel
                      active={sortColumn === column.id}
                      direction={sortDirection}
                      onClick={() => handleSort(column.id)}
                    >
                      {column.label}
                    </EnhancedSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </StyledTableHead>
          
          <TableBody>
            {loading ? (
              <TableSkeleton
                columns={columns.length + (selectable ? 1 : 0) + (expandable ? 1 : 0)}
                rows={pageSize}
              />
            ) : processedData.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length + (selectable ? 1 : 0) + (expandable ? 1 : 0)}
                  align="center"
                  sx={{ py: 8 }}
                >
                  <Typography variant="body1" color="text.secondary">
                    {emptyMessage}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              processedData.map((row, index) => {
                const isSelected = selectedRows.some(selected => selected === row);
                const isExpanded = expandedRows.has(index);
                
                return (
                  <React.Fragment key={index}>
                    <StyledTableRow
                      isSelected={isSelected}
                      isClickable={!!onRowClick}
                      onClick={() => onRowClick?.(row, index)}
                    >
                      {selectable && (
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={isSelected}
                            onChange={() => handleSelectRow(row)}
                            color="primary"
                            onClick={(e) => e.stopPropagation()}
                          />
                        </TableCell>
                      )}
                      
                      {expandable && (
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleExpandRow(index);
                            }}
                          >
                            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                          </IconButton>
                        </TableCell>
                      )}
                      
                      {columns.map((column) => {
                        const value = typeof column.accessor === 'function' 
                          ? column.accessor(row) 
                          : row[column.accessor];
                        
                        return (
                          <TableCell
                            key={column.id}
                            align={column.align || 'left'}
                          >
                            {column.render ? column.render(value, row, index) : value}
                          </TableCell>
                        );
                      })}
                    </StyledTableRow>
                    
                    {expandable && renderExpandedRow && (
                      <TableRow>
                        <TableCell
                          colSpan={columns.length + (selectable ? 1 : 0) + 1}
                          sx={{ py: 0, border: 0 }}
                        >
                          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                            <Box sx={{ py: 2 }}>
                              {renderExpandedRow(row, index)}
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    )}
                  </React.Fragment>
                );
              })
            )}
          </TableBody>
        </Table>
      </StyledTableContainer>
      
      {/* Pagination */}
      {pagination && !loading && (
        <TablePagination
          component="div"
          count={totalCount || processedData.length}
          page={page}
          onPageChange={(_, newPage) => onPageChange?.(newPage)}
          rowsPerPage={pageSize}
          onRowsPerPageChange={(event) => onPageSizeChange?.(parseInt(event.target.value, 10))}
          rowsPerPageOptions={[5, 10, 25, 50, 100]}
          labelRowsPerPage="Filas por página:"
          labelDisplayedRows={({ from, to, count }) => 
            `${from}-${to} de ${count !== -1 ? count : `más de ${to}`}`
          }
          sx={{
            borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            '& .MuiTablePagination-toolbar': {
              padding: theme.spacing(1, 3),
            },
          }}
        />
      )}
    </Paper>
  );
});

EnhancedTable.displayName = 'EnhancedTable';

export default EnhancedTable; 