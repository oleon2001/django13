import React, { createContext, useContext, useState, useRef, ReactNode } from 'react';

// ============================================================================
// MODAL TYPES - Tipos para modales
// ============================================================================

export interface Modal {
  id: string;
  component: React.ComponentType<any>;
  props?: Record<string, any>;
  options?: ModalOptions;
  isOpen: boolean;
  isClosing: boolean;
  zIndex: number;
}

export interface ModalOptions {
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  position?: 'center' | 'top' | 'bottom' | 'left' | 'right';
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
  showCloseButton?: boolean;
  showOverlay?: boolean;
  overlayClassName?: string;
  modalClassName?: string;
  animation?: 'fade' | 'slide' | 'zoom' | 'none';
  animationDuration?: number;
  preventScroll?: boolean;
  focusTrap?: boolean;
  autoFocus?: boolean;
  restoreFocus?: boolean;
  onOpen?: () => void;
  onClose?: () => void;
  onConfirm?: () => void;
  onCancel?: () => void;
}

export interface ModalContextType {
  // Estado
  modals: Modal[];
  activeModals: Modal[];
  
  // Métodos de apertura
  openModal: (component: React.ComponentType<any>, props?: Record<string, any>, options?: ModalOptions) => string;
  openConfirm: (title: string, message: string, options?: ModalOptions) => Promise<boolean>;
  openAlert: (title: string, message: string, options?: ModalOptions) => Promise<void>;
  openPrompt: (title: string, message: string, defaultValue?: string, options?: ModalOptions) => Promise<string | null>;
  
  // Métodos de cierre
  closeModal: (id: string) => void;
  closeAllModals: () => void;
  closeTopModal: () => void;
  
  // Métodos de actualización
  updateModal: (id: string, updates: Partial<Modal>) => void;
  updateModalProps: (id: string, props: Record<string, any>) => void;
  updateModalOptions: (id: string, options: Partial<ModalOptions>) => void;
  
  // Métodos de utilidad
  isModalOpen: (id: string) => boolean;
  getModal: (id: string) => Modal | null;
  getTopModal: () => Modal | null;
  getModalCount: () => number;
  hasModals: () => boolean;
  
  // Métodos de z-index
  getNextZIndex: () => number;
  bringToFront: (id: string) => void;
  
  // Métodos de bloqueo
  lockScroll: () => void;
  unlockScroll: () => void;
}

// ============================================================================
// MODAL CONTEXT - Contexto para modales
// ============================================================================

const ModalContext = createContext<ModalContextType | undefined>(undefined);

// ============================================================================
// MODAL PROVIDER - Provider para modales
// ============================================================================

interface ModalProviderProps {
  children: ReactNode;
  maxModals?: number;
  defaultZIndex?: number;
  zIndexIncrement?: number;
  enableFocusTrap?: boolean;
  enableScrollLock?: boolean;
  enableEscapeClose?: boolean;
  enableOverlayClose?: boolean;
}

export const ModalProvider: React.FC<ModalProviderProps> = ({
  children,
  maxModals = 10,
  defaultZIndex = 1000,
  zIndexIncrement = 10,
  enableFocusTrap = true,
  enableScrollLock = true,
  enableEscapeClose = true,
  enableOverlayClose = true,
}) => {
  const [modals, setModals] = useState<Modal[]>([]);
  const [nextZIndex, setNextZIndex] = useState(defaultZIndex);
  const scrollLockCountRef = useRef(0);

  // Generar ID único
  const generateId = (): string => {
    return `modal_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // Obtener siguiente z-index
  const getNextZIndex = (): number => {
    const zIndex = nextZIndex;
    setNextZIndex(prev => prev + zIndexIncrement);
    return zIndex;
  };

  // Bloquear scroll
  const lockScroll = (): void => {
    if (!enableScrollLock) return;
    
    scrollLockCountRef.current++;
    if (scrollLockCountRef.current === 1) {
      document.body.style.overflow = 'hidden';
      document.body.style.paddingRight = `${window.innerWidth - document.documentElement.clientWidth}px`;
    }
  };

  // Desbloquear scroll
  const unlockScroll = (): void => {
    if (!enableScrollLock) return;
    
    scrollLockCountRef.current = Math.max(0, scrollLockCountRef.current - 1);
    if (scrollLockCountRef.current === 0) {
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    }
  };

  // Obtener modales activos
  const activeModals = modals.filter(modal => modal.isOpen);

  // Abrir modal
  const openModal = (
    component: React.ComponentType<any>,
    props: Record<string, any> = {},
    options: ModalOptions = {}
  ): string => {
    const id = generateId();
    const zIndex = getNextZIndex();

    const modal: Modal = {
      id,
      component,
      props,
      options: {
        size: 'md',
        position: 'center',
        closeOnOverlayClick: enableOverlayClose,
        closeOnEscape: enableEscapeClose,
        showCloseButton: true,
        showOverlay: true,
        animation: 'fade',
        animationDuration: 300,
        preventScroll: enableScrollLock,
        focusTrap: enableFocusTrap,
        autoFocus: true,
        restoreFocus: true,
        ...options,
      },
      isOpen: true,
      isClosing: false,
      zIndex,
    };

    setModals(prev => {
      const updated = [...prev, modal];
      return updated.slice(-maxModals);
    });

    // Bloquear scroll si es necesario
    if (modal.options?.preventScroll) {
      lockScroll();
    }

    // Llamar callback onOpen
    if (modal.options?.onOpen) {
      modal.options.onOpen();
    }

    return id;
  };

  // Abrir confirmación
  const openConfirm = (title: string, message: string, options: ModalOptions = {}): Promise<boolean> => {
    return new Promise((resolve) => {
      const ConfirmModal: React.FC<{ onConfirm: () => void; onCancel: () => void }> = ({ onConfirm, onCancel }) => (
        <div className="modal-content">
          <div className="modal-header">
            <h3>{title}</h3>
          </div>
          <div className="modal-body">
            <p>{message}</p>
          </div>
          <div className="modal-footer">
            <button onClick={onCancel} className="btn btn-secondary">
              Cancel
            </button>
            <button onClick={onConfirm} className="btn btn-primary">
              Confirm
            </button>
          </div>
        </div>
      );

      const id = openModal(ConfirmModal, {}, {
        ...options,
        onConfirm: () => {
          closeModal(id);
          resolve(true);
        },
        onCancel: () => {
          closeModal(id);
          resolve(false);
        },
      });
    });
  };

  // Abrir alerta
  const openAlert = (title: string, message: string, options: ModalOptions = {}): Promise<void> => {
    return new Promise((resolve) => {
      const AlertModal: React.FC<{ onClose: () => void }> = ({ onClose }) => (
        <div className="modal-content">
          <div className="modal-header">
            <h3>{title}</h3>
          </div>
          <div className="modal-body">
            <p>{message}</p>
          </div>
          <div className="modal-footer">
            <button onClick={onClose} className="btn btn-primary">
              OK
            </button>
          </div>
        </div>
      );

      const id = openModal(AlertModal, {}, {
        ...options,
        onClose: () => {
          closeModal(id);
          resolve();
        },
      });
    });
  };

  // Abrir prompt
  const openPrompt = (
    title: string,
    message: string,
    defaultValue: string = '',
    options: ModalOptions = {}
  ): Promise<string | null> => {
    return new Promise((resolve) => {
      const PromptModal: React.FC<{ onConfirm: (value: string) => void; onCancel: () => void }> = ({ onConfirm, onCancel }) => {
        const [value, setValue] = React.useState(defaultValue);

        return (
          <div className="modal-content">
            <div className="modal-header">
              <h3>{title}</h3>
            </div>
            <div className="modal-body">
              <p>{message}</p>
              <input
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                className="form-control"
                autoFocus
              />
            </div>
            <div className="modal-footer">
              <button onClick={onCancel} className="btn btn-secondary">
                Cancel
              </button>
              <button onClick={() => onConfirm(value)} className="btn btn-primary">
                OK
              </button>
            </div>
          </div>
        );
      };

      const id = openModal(PromptModal, {}, {
        ...options,
        onConfirm: (value: string) => {
          closeModal(id);
          resolve(value);
        },
        onCancel: () => {
          closeModal(id);
          resolve(null);
        },
      });
    });
  };

  // Cerrar modal
  const closeModal = (id: string): void => {
    setModals(prev => {
      const modal = prev.find(m => m.id === id);
      if (!modal) return prev;

      // Marcar como cerrando
      const updated = prev.map(m =>
        m.id === id ? { ...m, isClosing: true } : m
      );

      // Llamar callback onClose
      if (modal.options?.onClose) {
        modal.options.onClose();
      }

      // Desbloquear scroll si es necesario
      if (modal.options?.preventScroll) {
        unlockScroll();
      }

      // Remover después de la animación
      setTimeout(() => {
        setModals(current => current.filter(m => m.id !== id));
      }, modal.options?.animationDuration || 300);

      return updated;
    });
  };

  // Cerrar todos los modales
  const closeAllModals = (): void => {
    setModals(prev => {
      prev.forEach(modal => {
        if (modal.options?.onClose) {
          modal.options.onClose();
        }
        if (modal.options?.preventScroll) {
          unlockScroll();
        }
      });
      return [];
    });
  };

  // Cerrar modal superior
  const closeTopModal = (): void => {
    const topModal = getTopModal();
    if (topModal) {
      closeModal(topModal.id);
    }
  };

  // Actualizar modal
  const updateModal = (id: string, updates: Partial<Modal>): void => {
    setModals(prev =>
      prev.map(modal =>
        modal.id === id ? { ...modal, ...updates } : modal
      )
    );
  };

  // Actualizar props del modal
  const updateModalProps = (id: string, props: Record<string, any>): void => {
    setModals(prev =>
      prev.map(modal =>
        modal.id === id ? { ...modal, props: { ...modal.props, ...props } } : modal
      )
    );
  };

  // Actualizar opciones del modal
  const updateModalOptions = (id: string, options: Partial<ModalOptions>): void => {
    setModals(prev =>
      prev.map(modal =>
        modal.id === id ? { ...modal, options: { ...modal.options, ...options } } : modal
      )
    );
  };

  // Verificar si modal está abierto
  const isModalOpen = (id: string): boolean => {
    return modals.some(modal => modal.id === id && modal.isOpen);
  };

  // Obtener modal
  const getModal = (id: string): Modal | null => {
    return modals.find(modal => modal.id === id) || null;
  };

  // Obtener modal superior
  const getTopModal = (): Modal | null => {
    const activeModals = modals.filter(modal => modal.isOpen);
    return activeModals.length > 0 ? activeModals[activeModals.length - 1] : null;
  };

  // Obtener conteo de modales
  const getModalCount = (): number => {
    return modals.filter(modal => modal.isOpen).length;
  };

  // Verificar si hay modales
  const hasModals = (): boolean => {
    return modals.some(modal => modal.isOpen);
  };

  // Traer al frente
  const bringToFront = (id: string): void => {
    const zIndex = getNextZIndex();
    updateModal(id, { zIndex });
  };

  const value: ModalContextType = {
    modals,
    activeModals,
    openModal,
    openConfirm,
    openAlert,
    openPrompt,
    closeModal,
    closeAllModals,
    closeTopModal,
    updateModal,
    updateModalProps,
    updateModalOptions,
    isModalOpen,
    getModal,
    getTopModal,
    getModalCount,
    hasModals,
    getNextZIndex,
    bringToFront,
    lockScroll,
    unlockScroll,
  };

  return (
    <ModalContext.Provider value={value}>
      {children}
    </ModalContext.Provider>
  );
};

// ============================================================================
// MODAL HOOK - Hook para usar el contexto de modales
// ============================================================================

export const useModal = () => {
  const context = useContext(ModalContext);
  
  if (context === undefined) {
    throw new Error('useModal must be used within a ModalProvider');
  }
  
  return context;
};

// ============================================================================
// MODAL HOOKS ESPECÍFICOS - Hooks para casos de uso específicos
// ============================================================================

export const useModalState = () => {
  const { modals, activeModals, hasModals, getModalCount } = useModal();
  return { modals, activeModals, hasModals, getModalCount };
};

export const useModalActions = () => {
  const { openModal, closeModal, closeAllModals, closeTopModal } = useModal();
  return { openModal, closeModal, closeAllModals, closeTopModal };
};

export const useModalHelpers = () => {
  const { openConfirm, openAlert, openPrompt } = useModal();
  return { openConfirm, openAlert, openPrompt };
}; 