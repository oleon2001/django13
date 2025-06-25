import React, { startTransition, useCallback } from 'react';

interface TransitionWrapperProps {
  children: React.ReactNode;
}

// Hook personalizado para manejar transiciones de manera segura
export const useTransitionSafe = () => {
  const safeStartTransition = useCallback((callback: () => void) => {
    try {
      startTransition(callback);
    } catch (error) {
      // Fallback para navegadores que no soportan startTransition
      console.warn('startTransition not supported, using immediate update:', error);
      callback();
    }
  }, []);

  return { safeStartTransition };
};

// Wrapper que proporciona contexto para transiciones seguras
const TransitionWrapper: React.FC<TransitionWrapperProps> = ({ children }) => {
  return (
    <React.Fragment>
      {children}
    </React.Fragment>
  );
};

export default TransitionWrapper; 