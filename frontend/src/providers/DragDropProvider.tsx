import React, { createContext, useContext, useState, useRef, ReactNode } from 'react';

// ============================================================================
// DRAG DROP TYPES - Tipos para drag and drop
// ============================================================================

export interface DragItem {
  id: string;
  type: string;
  data: any;
  source: string;
  index?: number;
}

export interface DropZone {
  id: string;
  type: string;
  accepts: string[];
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  data?: any;
  isActive: boolean;
  isOver: boolean;
  canDrop: boolean;
}

export interface DragState {
  isDragging: boolean;
  currentItem: DragItem | null;
  sourceZone: string | null;
  targetZone: string | null;
  mousePosition: {
    x: number;
    y: number;
  };
  dragOffset: {
    x: number;
    y: number;
  };
}

export interface DragDropContextType {
  // Estado
  dragState: DragState;
  dropZones: Map<string, DropZone>;
  
  // Métodos de drag
  startDrag: (item: DragItem, event: React.DragEvent | MouseEvent) => void;
  endDrag: () => void;
  updateDragPosition: (x: number, y: number) => void;
  
  // Métodos de drop zones
  registerDropZone: (zone: DropZone) => void;
  unregisterDropZone: (id: string) => void;
  updateDropZone: (id: string, updates: Partial<DropZone>) => void;
  getDropZone: (id: string) => DropZone | null;
  
  // Métodos de validación
  canDrop: (item: DragItem, zone: DropZone) => boolean;
  isOverZone: (zoneId: string) => boolean;
  getDropZonesForItem: (item: DragItem) => DropZone[];
  
  // Métodos de utilidad
  getDragItem: () => DragItem | null;
  isDragging: () => boolean;
  getCurrentDropZone: () => string | null;
  clearDragState: () => void;
  
  // Métodos de eventos
  handleDragStart: (item: DragItem) => (event: React.DragEvent) => void;
  handleDragEnd: () => (event: React.DragEvent) => void;
  handleDragOver: (zoneId: string) => (event: React.DragEvent) => void;
  handleDrop: (zoneId: string, onDrop?: (item: DragItem, zone: DropZone) => void) => (event: React.DragEvent) => void;
  
  // Métodos de mouse events
  handleMouseDown: (item: DragItem) => (event: React.MouseEvent) => void;
  handleMouseMove: () => (event: MouseEvent) => void;
  handleMouseUp: () => (event: MouseEvent) => void;
}

// ============================================================================
// DRAG DROP CONTEXT - Contexto para drag and drop
// ============================================================================

const DragDropContext = createContext<DragDropContextType | undefined>(undefined);

// ============================================================================
// DRAG DROP PROVIDER - Provider para drag and drop
// ============================================================================

interface DragDropProviderProps {
  children: ReactNode;
  enableMouseDrag?: boolean;
  enableKeyboardDrag?: boolean;
  dragThreshold?: number;
  dragDelay?: number;
  enableDragPreview?: boolean;
  enableDropIndicators?: boolean;
}

export const DragDropProvider: React.FC<DragDropProviderProps> = ({
  children,
  enableMouseDrag = true,
  enableKeyboardDrag = true,
  dragThreshold = 5,
  dragDelay = 200,
  enableDragPreview = true,
  enableDropIndicators = true,
}) => {
  const [dragState, setDragState] = useState<DragState>({
    isDragging: false,
    currentItem: null,
    sourceZone: null,
    targetZone: null,
    mousePosition: { x: 0, y: 0 },
    dragOffset: { x: 0, y: 0 },
  });

  const [dropZones, setDropZones] = useState<Map<string, DropZone>>(new Map());
  
  const dragStartPositionRef = useRef<{ x: number; y: number } | null>(null);
  const dragTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isMouseDraggingRef = useRef(false);

  // Iniciar drag
  const startDrag = (item: DragItem, event: React.DragEvent | MouseEvent): void => {
    const clientX = 'clientX' in event ? event.clientX : 0;
    const clientY = 'clientY' in event ? event.clientY : 0;

    dragStartPositionRef.current = { x: clientX, y: clientY };

    setDragState({
      isDragging: true,
      currentItem: item,
      sourceZone: item.source,
      targetZone: null,
      mousePosition: { x: clientX, y: clientY },
      dragOffset: { x: 0, y: 0 },
    });
  };

  // Finalizar drag
  const endDrag = (): void => {
    setDragState({
      isDragging: false,
      currentItem: null,
      sourceZone: null,
      targetZone: null,
      mousePosition: { x: 0, y: 0 },
      dragOffset: { x: 0, y: 0 },
    });

    dragStartPositionRef.current = null;
    isMouseDraggingRef.current = false;

    if (dragTimeoutRef.current) {
      clearTimeout(dragTimeoutRef.current);
      dragTimeoutRef.current = null;
    }
  };

  // Actualizar posición del drag
  const updateDragPosition = (x: number, y: number): void => {
    if (!dragState.isDragging || !dragStartPositionRef.current) return;

    const offsetX = x - dragStartPositionRef.current.x;
    const offsetY = y - dragStartPositionRef.current.y;

    setDragState(prev => ({
      ...prev,
      mousePosition: { x, y },
      dragOffset: { x: offsetX, y: offsetY },
    }));

    // Verificar drop zones
    const targetZone = findDropZoneAtPosition(x, y);
    if (targetZone !== dragState.targetZone) {
      setDragState(prev => ({
        ...prev,
        targetZone,
      }));
    }
  };

  // Encontrar drop zone en posición
  const findDropZoneAtPosition = (x: number, y: number): string | null => {
    for (const [id, zone] of dropZones) {
      const { position } = zone;
      if (
        x >= position.x &&
        x <= position.x + position.width &&
        y >= position.y &&
        y <= position.y + position.height
      ) {
        return id;
      }
    }
    return null;
  };

  // Registrar drop zone
  const registerDropZone = (zone: DropZone): void => {
    setDropZones(prev => {
      const newZones = new Map(prev);
      newZones.set(zone.id, zone);
      return newZones;
    });
  };

  // Desregistrar drop zone
  const unregisterDropZone = (id: string): void => {
    setDropZones(prev => {
      const newZones = new Map(prev);
      newZones.delete(id);
      return newZones;
    });
  };

  // Actualizar drop zone
  const updateDropZone = (id: string, updates: Partial<DropZone>): void => {
    setDropZones(prev => {
      const newZones = new Map(prev);
      const zone = newZones.get(id);
      if (zone) {
        newZones.set(id, { ...zone, ...updates });
      }
      return newZones;
    });
  };

  // Obtener drop zone
  const getDropZone = (id: string): DropZone | null => {
    return dropZones.get(id) || null;
  };

  // Verificar si se puede hacer drop
  const canDrop = (item: DragItem, zone: DropZone): boolean => {
    return zone.accepts.includes(item.type) && zone.isActive;
  };

  // Verificar si está sobre una zona
  const isOverZone = (zoneId: string): boolean => {
    return dragState.targetZone === zoneId;
  };

  // Obtener drop zones para un item
  const getDropZonesForItem = (item: DragItem): DropZone[] => {
    return Array.from(dropZones.values()).filter(zone => canDrop(item, zone));
  };

  // Obtener item actual
  const getDragItem = (): DragItem | null => {
    return dragState.currentItem;
  };

  // Verificar si está arrastrando
  const isDragging = (): boolean => {
    return dragState.isDragging;
  };

  // Obtener zona de drop actual
  const getCurrentDropZone = (): string | null => {
    return dragState.targetZone;
  };

  // Limpiar estado de drag
  const clearDragState = (): void => {
    endDrag();
  };

  // Manejar inicio de drag (HTML5)
  const handleDragStart = (item: DragItem) => (event: React.DragEvent): void => {
    event.stopPropagation();
    
    if (enableDragPreview) {
      // Crear preview personalizado
      const preview = document.createElement('div');
      preview.textContent = item.data?.label || item.id;
      preview.style.position = 'absolute';
      preview.style.top = '-1000px';
      preview.style.left = '-1000px';
      document.body.appendChild(preview);
      event.dataTransfer.setDragImage(preview, 0, 0);
      
      // Remover preview después de un momento
      setTimeout(() => {
        document.body.removeChild(preview);
      }, 0);
    }

    startDrag(item, event);
  };

  // Manejar fin de drag (HTML5)
  const handleDragEnd = () => (event: React.DragEvent): void => {
    event.stopPropagation();
    endDrag();
  };

  // Manejar drag over (HTML5)
  const handleDragOver = (zoneId: string) => (event: React.DragEvent): void => {
    event.preventDefault();
    event.stopPropagation();
    
    const zone = getDropZone(zoneId);
    if (!zone || !dragState.currentItem) return;

    const canDropHere = canDrop(dragState.currentItem, zone);
    
    updateDropZone(zoneId, {
      isOver: true,
      canDrop: canDropHere,
    });

    if (canDropHere) {
      event.dataTransfer.dropEffect = 'move';
    }
  };

  // Manejar drop (HTML5)
  const handleDrop = (zoneId: string, onDrop?: (item: DragItem, zone: DropZone) => void) => (event: React.DragEvent): void => {
    event.preventDefault();
    event.stopPropagation();
    
    const zone = getDropZone(zoneId);
    if (!zone || !dragState.currentItem) return;

    const canDropHere = canDrop(dragState.currentItem, zone);
    
    if (canDropHere && onDrop) {
      onDrop(dragState.currentItem, zone);
    }

    updateDropZone(zoneId, {
      isOver: false,
      canDrop: false,
    });

    endDrag();
  };

  // Manejar mouse down
  const handleMouseDown = (item: DragItem) => (event: React.MouseEvent): void => {
    if (!enableMouseDrag) return;
    
    event.preventDefault();
    event.stopPropagation();

    const startX = event.clientX;
    const startY = event.clientY;

    const handleMouseMove = (moveEvent: MouseEvent): void => {
      const deltaX = Math.abs(moveEvent.clientX - startX);
      const deltaY = Math.abs(moveEvent.clientY - startY);

      if (!isMouseDraggingRef.current && (deltaX > dragThreshold || deltaY > dragThreshold)) {
        isMouseDraggingRef.current = true;
        startDrag(item, moveEvent);
      }

      if (isMouseDraggingRef.current) {
        updateDragPosition(moveEvent.clientX, moveEvent.clientY);
      }
    };

    const handleMouseUp = (upEvent: MouseEvent): void => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      
      if (isMouseDraggingRef.current) {
        endDrag();
      }
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  // Manejar mouse move
  const handleMouseMove = () => (event: MouseEvent): void => {
    if (isMouseDraggingRef.current) {
      updateDragPosition(event.clientX, event.clientY);
    }
  };

  // Manejar mouse up
  const handleMouseUp = () => (event: MouseEvent): void => {
    if (isMouseDraggingRef.current) {
      endDrag();
    }
  };

  const value: DragDropContextType = {
    dragState,
    dropZones,
    startDrag,
    endDrag,
    updateDragPosition,
    registerDropZone,
    unregisterDropZone,
    updateDropZone,
    getDropZone,
    canDrop,
    isOverZone,
    getDropZonesForItem,
    getDragItem,
    isDragging,
    getCurrentDropZone,
    clearDragState,
    handleDragStart,
    handleDragEnd,
    handleDragOver,
    handleDrop,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
  };

  return (
    <DragDropContext.Provider value={value}>
      {children}
    </DragDropContext.Provider>
  );
};

// ============================================================================
// DRAG DROP HOOK - Hook para usar el contexto de drag and drop
// ============================================================================

export const useDragDrop = () => {
  const context = useContext(DragDropContext);
  
  if (context === undefined) {
    throw new Error('useDragDrop must be used within a DragDropProvider');
  }
  
  return context;
};

// ============================================================================
// DRAG DROP HOOKS ESPECÍFICOS - Hooks para casos de uso específicos
// ============================================================================

export const useDrag = (item: DragItem) => {
  const { handleDragStart, handleDragEnd, handleMouseDown } = useDragDrop();
  
  return {
    dragProps: {
      draggable: true,
      onDragStart: handleDragStart(item),
      onDragEnd: handleDragEnd(),
      onMouseDown: handleMouseDown(item),
    },
  };
};

export const useDrop = (zoneId: string, onDrop?: (item: DragItem, zone: DropZone) => void) => {
  const { handleDragOver, handleDrop, isOverZone, getDropZone } = useDragDrop();
  
  return {
    dropProps: {
      onDragOver: handleDragOver(zoneId),
      onDrop: handleDrop(zoneId, onDrop),
    },
    isOver: isOverZone(zoneId),
    zone: getDropZone(zoneId),
  };
};

export const useDragState = () => {
  const { dragState, isDragging, getDragItem, getCurrentDropZone } = useDragDrop();
  return {
    dragState,
    isDragging: isDragging(),
    currentItem: getDragItem(),
    currentDropZone: getCurrentDropZone(),
  };
}; 