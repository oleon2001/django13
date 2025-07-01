import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';

// ============================================================================
// FORM TYPES - Tipos para formularios
// ============================================================================

export type ValidationRule = 
  | { type: 'required'; message?: string }
  | { type: 'minLength'; value: number; message?: string }
  | { type: 'maxLength'; value: number; message?: string }
  | { type: 'min'; value: number; message?: string }
  | { type: 'max'; value: number; message?: string }
  | { type: 'email'; message?: string }
  | { type: 'url'; message?: string }
  | { type: 'pattern'; value: RegExp; message?: string }
  | { type: 'custom'; validator: (value: any) => boolean | string; message?: string }
  | { type: 'async'; validator: (value: any) => Promise<boolean | string>; message?: string };

export interface FormField {
  name: string;
  value: any;
  touched: boolean;
  dirty: boolean;
  error: string | null;
  isValidating: boolean;
  rules: ValidationRule[];
  initialValue: any;
  disabled: boolean;
  required: boolean;
}

export interface FormState {
  values: Record<string, any>;
  errors: Record<string, string | null>;
  touched: Record<string, boolean>;
  dirty: Record<string, boolean>;
  isValidating: Record<string, boolean>;
  isSubmitting: boolean;
  isDirty: boolean;
  isValid: boolean;
  submitCount: number;
  lastSubmitted: string | null;
}

export interface FormContextType {
  // Estado
  state: FormState;
  fields: Record<string, FormField>;
  
  // Métodos de valores
  getValue: (name: string) => any;
  setValue: (name: string, value: any) => void;
  setValues: (values: Record<string, any>) => void;
  reset: (values?: Record<string, any>) => void;
  
  // Métodos de validación
  validate: (name?: string) => Promise<boolean>;
  validateField: (name: string) => Promise<boolean>;
  validateAll: () => Promise<boolean>;
  setFieldError: (name: string, error: string | null) => void;
  clearErrors: (name?: string) => void;
  
  // Métodos de estado
  setTouched: (name: string, touched?: boolean) => void;
  setDirty: (name: string, dirty?: boolean) => void;
  setValidating: (name: string, isValidating: boolean) => void;
  
  // Métodos de configuración
  registerField: (name: string, options?: Partial<FormField>) => void;
  unregisterField: (name: string) => void;
  setFieldRules: (name: string, rules: ValidationRule[]) => void;
  setFieldRequired: (name: string, required: boolean) => void;
  setFieldDisabled: (name: string, disabled: boolean) => void;
  
  // Métodos de envío
  handleSubmit: (onSubmit: (values: Record<string, any>) => void | Promise<void>) => (e?: React.FormEvent) => void;
  submit: (onSubmit: (values: Record<string, any>) => void | Promise<void>) => Promise<void>;
  
  // Métodos de utilidad
  isFieldValid: (name: string) => boolean;
  isFieldTouched: (name: string) => boolean;
  isFieldDirty: (name: string) => boolean;
  isFieldRequired: (name: string) => boolean;
  isFieldDisabled: (name: string) => boolean;
  getFieldError: (name: string) => string | null;
  hasErrors: () => boolean;
  getErrors: () => Record<string, string>;
  
  // Métodos de transformación
  transform: (transformer: (values: Record<string, any>) => Record<string, any>) => void;
  transformField: (name: string, transformer: (value: any) => any) => void;
  
  // Métodos de utilidad
  getDirtyFields: () => string[];
  getTouchedFields: () => string[];
  getErrorFields: () => string[];
  getValidFields: () => string[];
}

// ============================================================================
// FORM CONTEXT - Contexto para formularios
// ============================================================================

const FormContext = createContext<FormContextType | undefined>(undefined);

// ============================================================================
// FORM PROVIDER - Provider para formularios
// ============================================================================

interface FormProviderProps {
  children: ReactNode;
  initialValues?: Record<string, any>;
  validationSchema?: Record<string, ValidationRule[]>;
  enableRealtimeValidation?: boolean;
  enableDirtyTracking?: boolean;
  enableTouchedTracking?: boolean;
  enableAsyncValidation?: boolean;
  validationDelay?: number;
}

export const FormProvider: React.FC<FormProviderProps> = ({
  children,
  initialValues = {},
  validationSchema = {},
  enableRealtimeValidation = true,
  enableDirtyTracking = true,
  enableTouchedTracking = true,
  enableAsyncValidation = true,
  validationDelay = 300,
}) => {
  const [state, setState] = useState<FormState>({
    values: { ...initialValues },
    errors: {},
    touched: {},
    dirty: {},
    isValidating: {},
    isSubmitting: false,
    isDirty: false,
    isValid: true,
    submitCount: 0,
    lastSubmitted: null,
  });

  const [fields, setFields] = useState<Record<string, FormField>>({});
  const validationTimeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // Validar valor según reglas
  const validateValue = async (value: any, rules: ValidationRule[]): Promise<string | null> => {
    for (const rule of rules) {
      let isValid: boolean | string = true;

      switch (rule.type) {
        case 'required':
          if (value === null || value === undefined || value === '') {
            isValid = rule.message || 'This field is required';
          }
          break;

        case 'minLength':
          if (value && value.length < rule.value) {
            isValid = rule.message || `Minimum length is ${rule.value} characters`;
          }
          break;

        case 'maxLength':
          if (value && value.length > rule.value) {
            isValid = rule.message || `Maximum length is ${rule.value} characters`;
          }
          break;

        case 'min':
          if (value !== null && value !== undefined && Number(value) < rule.value) {
            isValid = rule.message || `Minimum value is ${rule.value}`;
          }
          break;

        case 'max':
          if (value !== null && value !== undefined && Number(value) > rule.value) {
            isValid = rule.message || `Maximum value is ${rule.value}`;
          }
          break;

        case 'email':
          if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            isValid = rule.message || 'Invalid email format';
          }
          break;

        case 'url':
          if (value && !/^https?:\/\/.+/.test(value)) {
            isValid = rule.message || 'Invalid URL format';
          }
          break;

        case 'pattern':
          if (value && !rule.value.test(value)) {
            isValid = rule.message || 'Invalid format';
          }
          break;

        case 'custom':
          isValid = rule.validator(value);
          break;

        case 'async':
          if (enableAsyncValidation) {
            try {
              isValid = await rule.validator(value);
            } catch (error) {
              isValid = 'Validation failed';
            }
          }
          break;
      }

      if (isValid !== true) {
        return typeof isValid === 'string' ? isValid : rule.message || 'Invalid value';
      }
    }

    return null;
  };

  // Validar campo
  const validateField = async (name: string): Promise<boolean> => {
    const field = fields[name];
    if (!field) return true;

    setState(prev => ({
      ...prev,
      isValidating: { ...prev.isValidating, [name]: true },
    }));

    const error = await validateValue(field.value, field.rules);

    setState(prev => ({
      ...prev,
      errors: { ...prev.errors, [name]: error },
      isValidating: { ...prev.isValidating, [name]: false },
    }));

    setFields(prev => ({
      ...prev,
      [name]: { ...prev[name], error, isValidating: false },
    }));

    return !error;
  };

  // Validar todos los campos
  const validateAll = async (): Promise<boolean> => {
    const fieldNames = Object.keys(fields);
    const results = await Promise.all(fieldNames.map(validateField));
    return results.every(Boolean);
  };

  // Validar con delay para validación en tiempo real
  const validateWithDelay = (name: string) => {
    if (!enableRealtimeValidation) return;

    // Limpiar timeout anterior
    const existingTimeout = validationTimeoutsRef.current.get(name);
    if (existingTimeout) {
      clearTimeout(existingTimeout);
    }

    // Configurar nuevo timeout
    const timeout = setTimeout(() => {
      validateField(name);
      validationTimeoutsRef.current.delete(name);
    }, validationDelay);

    validationTimeoutsRef.current.set(name, timeout);
  };

  // Obtener valor
  const getValue = (name: string): any => {
    return state.values[name];
  };

  // Establecer valor
  const setValue = (name: string, value: any): void => {
    const field = fields[name];
    if (!field) return;

    const isDirty = enableDirtyTracking && value !== field.initialValue;
    const wasDirty = field.dirty;

    setState(prev => ({
      ...prev,
      values: { ...prev.values, [name]: value },
      dirty: { ...prev.dirty, [name]: isDirty },
      isDirty: prev.isDirty || isDirty,
    }));

    setFields(prev => ({
      ...prev,
      [name]: {
        ...prev[name],
        value,
        dirty: isDirty,
      },
    }));

    // Validar en tiempo real
    validateWithDelay(name);
  };

  // Establecer múltiples valores
  const setValues = (values: Record<string, any>): void => {
    setState(prev => ({
      ...prev,
      values: { ...prev.values, ...values },
    }));

    Object.entries(values).forEach(([name, value]) => {
      const field = fields[name];
      if (field) {
        const isDirty = enableDirtyTracking && value !== field.initialValue;
        
        setFields(prev => ({
          ...prev,
          [name]: {
            ...prev[name],
            value,
            dirty: isDirty,
          },
        }));

        validateWithDelay(name);
      }
    });
  };

  // Resetear formulario
  const reset = (values?: Record<string, any>): void => {
    const newValues = values || initialValues;
    
    setState({
      values: { ...newValues },
      errors: {},
      touched: {},
      dirty: {},
      isValidating: {},
      isSubmitting: false,
      isDirty: false,
      isValid: true,
      submitCount: 0,
      lastSubmitted: null,
    });

    setFields(prev => {
      const updatedFields: Record<string, FormField> = {};
      
      Object.keys(prev).forEach(name => {
        updatedFields[name] = {
          ...prev[name],
          value: newValues[name],
          touched: false,
          dirty: false,
          error: null,
          isValidating: false,
          initialValue: newValues[name],
        };
      });
      
      return updatedFields;
    });
  };

  // Establecer error de campo
  const setFieldError = (name: string, error: string | null): void => {
    setState(prev => ({
      ...prev,
      errors: { ...prev.errors, [name]: error },
    }));

    setFields(prev => ({
      ...prev,
      [name]: { ...prev[name], error },
    }));
  };

  // Limpiar errores
  const clearErrors = (name?: string): void => {
    if (name) {
      setFieldError(name, null);
    } else {
      setState(prev => ({
        ...prev,
        errors: {},
      }));

      setFields(prev => {
        const updatedFields: Record<string, FormField> = {};
        Object.keys(prev).forEach(key => {
          updatedFields[key] = { ...prev[key], error: null };
        });
        return updatedFields;
      });
    }
  };

  // Establecer touched
  const setTouched = (name: string, touched = true): void => {
    if (!enableTouchedTracking) return;

    setState(prev => ({
      ...prev,
      touched: { ...prev.touched, [name]: touched },
    }));

    setFields(prev => ({
      ...prev,
      [name]: { ...prev[name], touched },
    }));
  };

  // Establecer dirty
  const setDirty = (name: string, dirty = true): void => {
    if (!enableDirtyTracking) return;

    setState(prev => ({
      ...prev,
      dirty: { ...prev.dirty, [name]: dirty },
      isDirty: prev.isDirty || dirty,
    }));

    setFields(prev => ({
      ...prev,
      [name]: { ...prev[name], dirty },
    }));
  };

  // Establecer validating
  const setValidating = (name: string, isValidating: boolean): void => {
    setState(prev => ({
      ...prev,
      isValidating: { ...prev.isValidating, [name]: isValidating },
    }));

    setFields(prev => ({
      ...prev,
      [name]: { ...prev[name], isValidating },
    }));
  };

  // Registrar campo
  const registerField = (name: string, options: Partial<FormField> = {}): void => {
    const field: FormField = {
      name,
      value: options.value ?? initialValues[name],
      touched: false,
      dirty: false,
      error: null,
      isValidating: false,
      rules: options.rules ?? validationSchema[name] ?? [],
      initialValue: options.initialValue ?? initialValues[name],
      disabled: options.disabled ?? false,
      required: options.required ?? false,
    };

    setFields(prev => ({
      ...prev,
      [name]: field,
    }));
  };

  // Desregistrar campo
  const unregisterField = (name: string): void => {
    setFields(prev => {
      const { [name]: removed, ...rest } = prev;
      return rest;
    });

    setState(prev => {
      const { [name]: removedValue, ...restValues } = prev.values;
      const { [name]: removedError, ...restErrors } = prev.errors;
      const { [name]: removedTouched, ...restTouched } = prev.touched;
      const { [name]: removedDirty, ...restDirty } = prev.dirty;
      const { [name]: removedValidating, ...restValidating } = prev.isValidating;

      return {
        ...prev,
        values: restValues,
        errors: restErrors,
        touched: restTouched,
        dirty: restDirty,
        isValidating: restValidating,
      };
    });
  };

  // Establecer reglas de campo
  const setFieldRules = (name: string, rules: ValidationRule[]): void => {
    setFields(prev => ({
      ...prev,
      [name]: { ...prev[name], rules },
    }));
  };

  // Establecer campo requerido
  const setFieldRequired = (name: string, required: boolean): void => {
    setFields(prev => ({
      ...prev,
      [name]: { ...prev[name], required },
    }));
  };

  // Establecer campo deshabilitado
  const setFieldDisabled = (name: string, disabled: boolean): void => {
    setFields(prev => ({
      ...prev,
      [name]: { ...prev[name], disabled },
    }));
  };

  // Manejar envío
  const handleSubmit = (onSubmit: (values: Record<string, any>) => void | Promise<void>) => {
    return async (e?: React.FormEvent) => {
      if (e) {
        e.preventDefault();
      }

      setState(prev => ({
        ...prev,
        isSubmitting: true,
        submitCount: prev.submitCount + 1,
        lastSubmitted: new Date().toISOString(),
      }));

      try {
        const isValid = await validateAll();
        if (isValid) {
          await onSubmit(state.values);
        }
      } catch (error) {
        console.error('Form submission error:', error);
      } finally {
        setState(prev => ({
          ...prev,
          isSubmitting: false,
        }));
      }
    };
  };

  // Enviar formulario
  const submit = async (onSubmit: (values: Record<string, any>) => void | Promise<void>): Promise<void> => {
    setState(prev => ({
      ...prev,
      isSubmitting: true,
      submitCount: prev.submitCount + 1,
      lastSubmitted: new Date().toISOString(),
    }));

    try {
      const isValid = await validateAll();
      if (isValid) {
        await onSubmit(state.values);
      }
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setState(prev => ({
        ...prev,
        isSubmitting: false,
      }));
    }
  };

  // Verificar si campo es válido
  const isFieldValid = (name: string): boolean => {
    return !state.errors[name];
  };

  // Verificar si campo está touched
  const isFieldTouched = (name: string): boolean => {
    return state.touched[name] || false;
  };

  // Verificar si campo está dirty
  const isFieldDirty = (name: string): boolean => {
    return state.dirty[name] || false;
  };

  // Verificar si campo es requerido
  const isFieldRequired = (name: string): boolean => {
    return fields[name]?.required || false;
  };

  // Verificar si campo está deshabilitado
  const isFieldDisabled = (name: string): boolean => {
    return fields[name]?.disabled || false;
  };

  // Obtener error de campo
  const getFieldError = (name: string): string | null => {
    return state.errors[name] || null;
  };

  // Verificar si hay errores
  const hasErrors = (): boolean => {
    return Object.values(state.errors).some(Boolean);
  };

  // Obtener errores
  const getErrors = (): Record<string, string> => {
    return state.errors;
  };

  // Transformar valores
  const transform = (transformer: (values: Record<string, any>) => Record<string, any>): void => {
    const transformedValues = transformer(state.values);
    setValues(transformedValues);
  };

  // Transformar campo
  const transformField = (name: string, transformer: (value: any) => any): void => {
    const currentValue = getValue(name);
    const transformedValue = transformer(currentValue);
    setValue(name, transformedValue);
  };

  // Obtener campos dirty
  const getDirtyFields = (): string[] => {
    return Object.entries(state.dirty)
      .filter(([, isDirty]) => isDirty)
      .map(([name]) => name);
  };

  // Obtener campos touched
  const getTouchedFields = (): string[] => {
    return Object.entries(state.touched)
      .filter(([, isTouched]) => isTouched)
      .map(([name]) => name);
  };

  // Obtener campos con errores
  const getErrorFields = (): string[] => {
    return Object.entries(state.errors)
      .filter(([, error]) => error)
      .map(([name]) => name);
  };

  // Obtener campos válidos
  const getValidFields = (): string[] => {
    return Object.keys(fields).filter(name => !state.errors[name]);
  };

  // Validar
  const validate = async (name?: string): Promise<boolean> => {
    if (name) {
      return validateField(name);
    }
    return validateAll();
  };

  const value: FormContextType = {
    state,
    fields,
    getValue,
    setValue,
    setValues,
    reset,
    validate,
    validateField,
    validateAll,
    setFieldError,
    clearErrors,
    setTouched,
    setDirty,
    setValidating,
    registerField,
    unregisterField,
    setFieldRules,
    setFieldRequired,
    setFieldDisabled,
    handleSubmit,
    submit,
    isFieldValid,
    isFieldTouched,
    isFieldDirty,
    isFieldRequired,
    isFieldDisabled,
    getFieldError,
    hasErrors,
    getErrors,
    transform,
    transformField,
    getDirtyFields,
    getTouchedFields,
    getErrorFields,
    getValidFields,
  };

  return (
    <FormContext.Provider value={value}>
      {children}
    </FormContext.Provider>
  );
};

// ============================================================================
// FORM HOOK - Hook para usar el contexto de formularios
// ============================================================================

export const useForm = () => {
  const context = useContext(FormContext);
  
  if (context === undefined) {
    throw new Error('useForm must be used within a FormProvider');
  }
  
  return context;
};

// ============================================================================
// FORM HOOKS ESPECÍFICOS - Hooks para casos de uso específicos
// ============================================================================

export const useFormField = (name: string) => {
  const {
    getValue,
    setValue,
    isFieldValid,
    isFieldTouched,
    isFieldDirty,
    isFieldRequired,
    isFieldDisabled,
    getFieldError,
    setTouched,
    setDirty,
  } = useForm();

  return {
    value: getValue(name),
    setValue: (value: any) => setValue(name, value),
    isValid: isFieldValid(name),
    isTouched: isFieldTouched(name),
    isDirty: isFieldDirty(name),
    isRequired: isFieldRequired(name),
    isDisabled: isFieldDisabled(name),
    error: getFieldError(name),
    setTouched: (touched?: boolean) => setTouched(name, touched),
    setDirty: (dirty?: boolean) => setDirty(name, dirty),
  };
};

export const useFormValidation = () => {
  const { validate, validateField, validateAll, hasErrors, getErrors } = useForm();
  return { validate, validateField, validateAll, hasErrors, getErrors };
};

export const useFormSubmission = () => {
  const { handleSubmit, submit, state } = useForm();
  return { handleSubmit, submit, isSubmitting: state.isSubmitting };
}; 