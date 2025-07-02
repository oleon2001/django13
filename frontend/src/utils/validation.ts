import React from 'react';

// Tipos para validación
export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => string | null;
}

export interface ValidationRules {
  [key: string]: ValidationRule;
}

export interface ValidationErrors {
  [key: string]: string;
}

// Validadores comunes
export const validators = {
  // Validar campo requerido
  required: (value: any): string | null => {
    if (value === null || value === undefined || value === '') {
      return 'Este campo es requerido';
    }
    return null;
  },

  // Validar longitud mínima
  minLength: (min: number) => (value: string): string | null => {
    if (value && value.length < min) {
      return `Mínimo ${min} caracteres`;
    }
    return null;
  },

  // Validar longitud máxima
  maxLength: (max: number) => (value: string): string | null => {
    if (value && value.length > max) {
      return `Máximo ${max} caracteres`;
    }
    return null;
  },

  // Validar patrón (regex)
  pattern: (regex: RegExp, message: string) => (value: string): string | null => {
    if (value && !regex.test(value)) {
      return message;
    }
    return null;
  },

  // Validar email
  email: (value: string): string | null => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (value && !emailRegex.test(value)) {
      return 'Email inválido';
    }
    return null;
  },

  // Validar teléfono
  phone: (value: string): string | null => {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    if (value && !phoneRegex.test(value.replace(/\s/g, ''))) {
      return 'Teléfono inválido';
    }
    return null;
  },

  // Validar IMEI
  imei: (value: string): string | null => {
    const imeiRegex = /^\d{15}$/;
    if (value && !imeiRegex.test(value)) {
      return 'IMEI debe tener 15 dígitos';
    }
    return null;
  },

  // Validar coordenadas
  coordinates: (value: number): string | null => {
    if (value < -180 || value > 180) {
      return 'Coordenada debe estar entre -180 y 180';
    }
    return null;
  },

  // Validar latitud
  latitude: (value: number): string | null => {
    if (value < -90 || value > 90) {
      return 'Latitud debe estar entre -90 y 90';
    }
    return null;
  },

  // Validar longitud
  longitude: (value: number): string | null => {
    if (value < -180 || value > 180) {
      return 'Longitud debe estar entre -180 y 180';
    }
    return null;
  },

  // Validar número positivo
  positive: (value: number): string | null => {
    if (value <= 0) {
      return 'Debe ser un número positivo';
    }
    return null;
  },

  // Validar número entero
  integer: (value: number): string | null => {
    if (!Number.isInteger(value)) {
      return 'Debe ser un número entero';
    }
    return null;
  },

  // Validar fecha futura
  futureDate: (value: Date): string | null => {
    if (value <= new Date()) {
      return 'La fecha debe ser futura';
    }
    return null;
  },

  // Validar fecha pasada
  pastDate: (value: Date): string | null => {
    if (value >= new Date()) {
      return 'La fecha debe ser pasada';
    }
    return null;
  },

  // Validar URL
  url: (value: string): string | null => {
    try {
      new URL(value);
      return null;
    } catch {
      return 'URL inválida';
    }
  },

  // Validar que dos campos sean iguales
  match: (fieldName: string) => (value: any, allValues: any): string | null => {
    if (value !== allValues[fieldName]) {
      return `Debe coincidir con ${fieldName}`;
    }
    return null;
  },
};

// Función principal de validación
export const validateField = (
  value: any,
  rules: ValidationRule,
  allValues?: any
): string | null => {
  // Validar requerido
  if (rules.required && validators.required(value)) {
    return validators.required(value);
  }

  // Si el campo no es requerido y está vacío, no validar más
  if (!rules.required && (value === null || value === undefined || value === '')) {
    return null;
  }

  // Validar longitud mínima
  if (rules.minLength && typeof value === 'string') {
    const error = validators.minLength(rules.minLength)(value);
    if (error) return error;
  }

  // Validar longitud máxima
  if (rules.maxLength && typeof value === 'string') {
    const error = validators.maxLength(rules.maxLength)(value);
    if (error) return error;
  }

  // Validar patrón
  if (rules.pattern && typeof value === 'string') {
    const error = validators.pattern(rules.pattern, 'Formato inválido')(value);
    if (error) return error;
  }

  // Validar función personalizada
  if (rules.custom) {
    const error = rules.custom(value);
    if (error) return error;
  }

  return null;
};

// Validar formulario completo
export const validateForm = (
  values: any,
  rules: ValidationRules
): ValidationErrors => {
  const errors: ValidationErrors = {};

  Object.keys(rules).forEach(fieldName => {
    const fieldRules = rules[fieldName];
    const fieldValue = values[fieldName];
    
    const error = validateField(fieldValue, fieldRules, values);
    if (error) {
      errors[fieldName] = error;
    }
  });

  return errors;
};

// Reglas de validación predefinidas
export const validationSchemas = {
  // Esquema para dispositivos GPS
  device: {
    imei: { required: true, custom: validators.imei },
    name: { required: true, minLength: 2, maxLength: 100 },
    phone_number: { required: true, custom: validators.phone },
    description: { maxLength: 500 },
    latitude: { custom: validators.latitude },
    longitude: { custom: validators.longitude },
  },

  // Esquema para vehículos
  vehicle: {
    plate_number: { required: true, minLength: 3, maxLength: 20 },
    brand: { required: true, minLength: 2, maxLength: 50 },
    model: { required: true, minLength: 2, maxLength: 50 },
    year: { required: true, custom: validators.integer },
    color: { required: true, minLength: 2, maxLength: 30 },
    description: { maxLength: 500 },
  },

  // Esquema para conductores
  driver: {
    first_name: { required: true, minLength: 2, maxLength: 50 },
    last_name: { required: true, minLength: 2, maxLength: 50 },
    email: { required: true, custom: validators.email },
    phone: { required: true, custom: validators.phone },
    license_number: { required: true, minLength: 5, maxLength: 20 },
    license_expiry: { required: true, custom: validators.futureDate },
  },

  // Esquema para geocercas
  geofence: {
    name: { required: true, minLength: 2, maxLength: 100 },
    description: { maxLength: 500 },
    latitude: { required: true, custom: validators.latitude },
    longitude: { required: true, custom: validators.longitude },
    radius: { required: true, custom: validators.positive },
  },

  // Esquema para usuarios
  user: {
    username: { required: true, minLength: 3, maxLength: 50 },
    email: { required: true, custom: validators.email },
    password: { required: true, minLength: 8 },
    confirm_password: { required: true, custom: validators.match('password') },
    first_name: { required: true, minLength: 2, maxLength: 50 },
    last_name: { required: true, minLength: 2, maxLength: 50 },
  },

  // Esquema para login
  login: {
    username: { required: true },
    password: { required: true },
  },
};

// Función para validar en tiempo real
export const validateFieldRealTime = (
  fieldName: string,
  value: any,
  rules: ValidationRules,
  allValues?: any
): string | null => {
  const fieldRules = rules[fieldName];
  if (!fieldRules) return null;

  return validateField(value, fieldRules, allValues);
};

// Función para limpiar errores de un campo específico
export const clearFieldError = (
  errors: ValidationErrors,
  fieldName: string
): ValidationErrors => {
  const newErrors = { ...errors };
  delete newErrors[fieldName];
  return newErrors;
};

// Función para verificar si el formulario es válido
export const isFormValid = (errors: ValidationErrors): boolean => {
  return Object.keys(errors).length === 0;
};

// Función para obtener el primer error
export const getFirstError = (errors: ValidationErrors): string | null => {
  const firstKey = Object.keys(errors)[0];
  return firstKey ? errors[firstKey] : null;
};

// Función para formatear errores para mostrar
export const formatErrors = (errors: ValidationErrors): string[] => {
  return Object.values(errors);
};

// Hook personalizado para validación (para usar en componentes)
export const useValidation = (rules: ValidationRules) => {
  const [errors, setErrors] = React.useState<ValidationErrors>({});
  const [touched, setTouched] = React.useState<Record<string, boolean>>({});

  const validateField = React.useCallback((
    fieldName: string,
    value: any,
    allValues?: any
  ) => {
    const error = validateFieldRealTime(fieldName, value, rules, allValues);
    
    setErrors(prev => {
      const newErrors = { ...prev };
      if (error) {
        newErrors[fieldName] = error;
      } else {
        delete newErrors[fieldName];
      }
      return newErrors;
    });

    return error;
  }, [rules]);

  const validateFormCallback = React.useCallback((values: any) => {
    const newErrors = validateForm(values, rules);
    setErrors(newErrors);
    return newErrors;
  }, [rules]);

  const setFieldTouched = React.useCallback((fieldName: string, isTouched = true) => {
    setTouched(prev => ({
      ...prev,
      [fieldName]: isTouched,
    }));
  }, []);

  const clearErrors = React.useCallback(() => {
    setErrors({});
  }, []);

  const clearFieldError = React.useCallback((fieldName: string) => {
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[fieldName];
      return newErrors;
    });
  }, []);

  return {
    errors,
    touched,
    validateField,
    validateForm: validateFormCallback,
    setFieldTouched,
    clearErrors,
    clearFieldError,
    isValid: isFormValid(errors),
  };
}; 