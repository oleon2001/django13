import React, { memo, useCallback, useMemo, useState } from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  FormLabel,
  FormHelperText,
  InputAdornment,
  IconButton,
  Typography,
  Fade,
  Grow,
  Alert,
  LinearProgress,
  useTheme,
  alpha,
  Checkbox,
  FormControlLabel,
  Radio,
  RadioGroup,
  Switch,
  Slider,
  Rating,
  Select,
  MenuItem,
  InputLabel,
} from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';
import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

// Enhanced animations
const formAnimations = {
  slideIn: keyframes`
    from { transform: translateX(-20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  `,
  
  shake: keyframes`
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  `,
  
  success: keyframes`
    0% { transform: scale(0.8); opacity: 0; }
    50% { transform: scale(1.1); opacity: 1; }
    100% { transform: scale(1); opacity: 1; }
  `,
};

// Enhanced Form Container
const FormContainer = styled(Box)(({ theme }) => ({
  width: '100%',
  maxWidth: 600,
  margin: '0 auto',
  padding: theme.spacing(3),
  borderRadius: theme.spacing(2),
  background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.9)} 0%, ${alpha(theme.palette.background.paper, 0.7)} 100%)`,
  backdropFilter: 'blur(20px)',
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.08)}`,
}));

// Enhanced TextField with better validation states
const StyledTextField = styled(TextField, {
  shouldForwardProp: (prop) => !['hasError', 'hasSuccess'].includes(prop as string),
})<{ hasError?: boolean; hasSuccess?: boolean }>(({ theme, hasError, hasSuccess }) => ({
  '& .MuiOutlinedInput-root': {
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    
    ...(hasError && {
      '& fieldset': {
        borderColor: theme.palette.error.main,
        borderWidth: 2,
      },
      '&:hover fieldset': {
        borderColor: theme.palette.error.dark,
      },
      animation: `${formAnimations.shake} 0.5s ease-in-out`,
    }),
    
    ...(hasSuccess && {
      '& fieldset': {
        borderColor: theme.palette.success.main,
        borderWidth: 2,
      },
      '&:hover fieldset': {
        borderColor: theme.palette.success.dark,
      },
    }),
    
    '&.Mui-focused fieldset': {
      borderWidth: 2,
      borderColor: hasError 
        ? theme.palette.error.main 
        : hasSuccess 
        ? theme.palette.success.main 
        : theme.palette.primary.main,
    },
  },
  
  '& .MuiInputLabel-root': {
    ...(hasError && {
      color: theme.palette.error.main,
    }),
    ...(hasSuccess && {
      color: theme.palette.success.main,
    }),
  },
}));

// Form Field Container with enhanced layout
const FieldContainer = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  position: 'relative',
  
  '&:last-child': {
    marginBottom: 0,
  },
}));

// Success/Error Icons
const ValidationIcon = styled(Box)<{ type: 'success' | 'error' }>(
  ({ theme, type }) => ({
    position: 'absolute',
    right: theme.spacing(1),
    top: '50%',
    transform: 'translateY(-50%)',
    zIndex: 1,
    
    '& .MuiSvgIcon-root': {
      fontSize: '1.25rem',
      color: theme.palette[type].main,
      animation: type === 'success' ? `${formAnimations.success} 0.6s ease-out` : 'none',
    },
  })
);

// Enhanced Button with loading states
const SubmitButton = styled(Button)(({ theme }) => ({
  minHeight: 48,
  borderRadius: theme.spacing(1.5),
  fontWeight: 600,
  textTransform: 'none',
  fontSize: '1rem',
  boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.3)}`,
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: `0 6px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
  },
  
  '&:active': {
    transform: 'translateY(0)',
  },
  
  '&.Mui-disabled': {
    transform: 'none',
    boxShadow: 'none',
  },
}));

// Field Types
export interface BaseFieldProps {
  name: string;
  label: string;
  placeholder?: string;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  validation?: (value: any) => string | null;
}

export interface TextFieldProps extends BaseFieldProps {
  type: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  multiline?: boolean;
  rows?: number;
  maxLength?: number;
}

export interface SelectFieldProps extends BaseFieldProps {
  type: 'select';
  options: Array<{ value: string | number; label: string }>;
  multiple?: boolean;
}

export interface CheckboxFieldProps extends BaseFieldProps {
  type: 'checkbox';
}

export interface RadioFieldProps extends BaseFieldProps {
  type: 'radio';
  options: Array<{ value: string | number; label: string }>;
  row?: boolean;
}

export interface SwitchFieldProps extends BaseFieldProps {
  type: 'switch';
}

export interface SliderFieldProps extends BaseFieldProps {
  type: 'slider';
  min?: number;
  max?: number;
  step?: number;
}

export interface RatingFieldProps extends BaseFieldProps {
  type: 'rating';
  max?: number;
}

export type FieldConfig = 
  | TextFieldProps 
  | SelectFieldProps 
  | CheckboxFieldProps 
  | RadioFieldProps 
  | SwitchFieldProps 
  | SliderFieldProps 
  | RatingFieldProps;

// Enhanced Form Props
export interface EnhancedFormProps {
  fields: FieldConfig[];
  onSubmit: (data: Record<string, any>) => Promise<void> | void;
  onCancel?: () => void;
  submitLabel?: string;
  cancelLabel?: string;
  loading?: boolean;
  disabled?: boolean;
  defaultValues?: Record<string, any>;
  title?: string;
  description?: string;
  showProgress?: boolean;
  className?: string;
  sx?: object;
}

// Field Renderer Component
const FieldRenderer = memo<{
  field: FieldConfig;
  value: any;
  error: string | null;
  onChange: (value: any) => void;
  onBlur: () => void;
}>(({ field, value, error, onChange, onBlur }) => {
  const [showPassword, setShowPassword] = useState(false);
  
  const hasError = !!error;
  const hasSuccess = !hasError && value && field.required;
  
  const togglePasswordVisibility = useCallback(() => {
    setShowPassword(prev => !prev);
  }, []);
  
  const renderValidationIcon = () => {
    if (hasError) {
      return (
        <ValidationIcon type="error">
          <ErrorIcon />
        </ValidationIcon>
      );
    }
    
    if (hasSuccess) {
      return (
        <ValidationIcon type="success">
          <CheckCircleIcon />
        </ValidationIcon>
      );
    }
    
    return null;
  };
  
  const renderField = () => {
    switch (field.type) {
      case 'text':
      case 'email':
      case 'number':
      case 'tel':
      case 'url':
        return (
          <Box sx={{ position: 'relative' }}>
            <StyledTextField
              type={field.type}
              label={field.label}
              placeholder={field.placeholder}
              value={value || ''}
              onChange={(e) => onChange(e.target.value)}
              onBlur={onBlur}
              error={hasError}
              helperText={error || field.helperText}
              required={field.required}
              disabled={field.disabled}
              fullWidth={field.fullWidth !== false}
              multiline={field.multiline}
              rows={field.rows}
              hasError={hasError}
              hasSuccess={hasSuccess}
              inputProps={{
                maxLength: field.maxLength,
              }}
            />
            {renderValidationIcon()}
          </Box>
        );
        
      case 'password':
        return (
          <Box sx={{ position: 'relative' }}>
            <StyledTextField
              type={showPassword ? 'text' : 'password'}
              label={field.label}
              placeholder={field.placeholder}
              value={value || ''}
              onChange={(e) => onChange(e.target.value)}
              onBlur={onBlur}
              error={hasError}
              helperText={error || field.helperText}
              required={field.required}
              disabled={field.disabled}
              fullWidth={field.fullWidth !== false}
              hasError={hasError}
              hasSuccess={hasSuccess}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={togglePasswordVisibility} edge="end">
                      {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            {renderValidationIcon()}
          </Box>
        );
        
      case 'select':
        return (
          <FormControl fullWidth={field.fullWidth !== false} error={hasError}>
            <InputLabel>{field.label}</InputLabel>
            <Select
              value={value || (field.multiple ? [] : '')}
              onChange={(e) => onChange(e.target.value)}
              onBlur={onBlur}
              label={field.label}
              multiple={field.multiple}
              disabled={field.disabled}
            >
              {field.options.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
            {(error || field.helperText) && (
              <FormHelperText>
                {error || field.helperText}
              </FormHelperText>
            )}
          </FormControl>
        );
        
      case 'checkbox':
        return (
          <FormControl error={hasError}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={value || false}
                  onChange={(e) => onChange(e.target.checked)}
                  onBlur={onBlur}
                  disabled={field.disabled}
                />
              }
              label={field.label}
            />
            {(error || field.helperText) && (
              <FormHelperText>
                {error || field.helperText}
              </FormHelperText>
            )}
          </FormControl>
        );
        
      case 'radio':
        return (
          <FormControl error={hasError}>
            <FormLabel>{field.label}</FormLabel>
            <RadioGroup
              value={value || ''}
              onChange={(e) => onChange(e.target.value)}
              onBlur={onBlur}
              row={field.row}
            >
              {field.options.map((option) => (
                <FormControlLabel
                  key={option.value}
                  value={option.value}
                  control={<Radio disabled={field.disabled} />}
                  label={option.label}
                />
              ))}
            </RadioGroup>
            {(error || field.helperText) && (
              <FormHelperText>
                {error || field.helperText}
              </FormHelperText>
            )}
          </FormControl>
        );
        
      case 'switch':
        return (
          <FormControl error={hasError}>
            <FormControlLabel
              control={
                <Switch
                  checked={value || false}
                  onChange={(e) => onChange(e.target.checked)}
                  onBlur={onBlur}
                  disabled={field.disabled}
                />
              }
              label={field.label}
            />
            {(error || field.helperText) && (
              <FormHelperText>
                {error || field.helperText}
              </FormHelperText>
            )}
          </FormControl>
        );
        
      case 'slider':
        return (
          <FormControl fullWidth error={hasError}>
            <FormLabel sx={{ mb: 2 }}>{field.label}</FormLabel>
            <Slider
              value={value || field.min || 0}
              onChange={(_, newValue) => onChange(newValue)}
              onBlur={onBlur}
              min={field.min}
              max={field.max}
              step={field.step}
              disabled={field.disabled}
              valueLabelDisplay="auto"
            />
            {(error || field.helperText) && (
              <FormHelperText>
                {error || field.helperText}
              </FormHelperText>
            )}
          </FormControl>
        );
        
      case 'rating':
        return (
          <FormControl error={hasError}>
            <FormLabel sx={{ mb: 1 }}>{field.label}</FormLabel>
            <Rating
              value={value || 0}
              onChange={(_, newValue) => onChange(newValue)}
              onBlur={onBlur}
              max={field.max}
              disabled={field.disabled}
            />
            {(error || field.helperText) && (
              <FormHelperText>
                {error || field.helperText}
              </FormHelperText>
            )}
          </FormControl>
        );
        
      default:
        return null;
    }
  };
  
  return (
    <FieldContainer>
      <Fade in timeout={300}>
        <div>{renderField()}</div>
      </Fade>
    </FieldContainer>
  );
});

FieldRenderer.displayName = 'FieldRenderer';

// Main Enhanced Form Component
const EnhancedForm = memo<EnhancedFormProps>(({
  fields,
  onSubmit,
  onCancel,
  submitLabel = 'Enviar',
  cancelLabel = 'Cancelar',
  loading = false,
  disabled = false,
  defaultValues = {},
  title,
  description,
  showProgress = false,
  className,
  sx,
}) => {
  const theme = useTheme();
  const [formData, setFormData] = useState<Record<string, any>>(defaultValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<boolean>(false);
  
  const handleFieldChange = useCallback((fieldName: string, value: any) => {
    setFormData(prev => ({ ...prev, [fieldName]: value }));
    
    // Clear error when user starts typing
    if (errors[fieldName]) {
      setErrors(prev => ({ ...prev, [fieldName]: '' }));
    }
  }, [errors]);
  
  const handleFieldBlur = useCallback((fieldName: string) => {
    setTouched(prev => ({ ...prev, [fieldName]: true }));
    
    const field = fields.find(f => f.name === fieldName);
    if (!field) return;
    
    const value = formData[fieldName];
    let error: string | null = null;
    
    // Required validation
    if (field.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
      error = `${field.label} es requerido`;
    }
    
    // Custom validation
    if (!error && field.validation && value) {
      error = field.validation(value);
    }
    
    // Built-in validations
    if (!error && value && typeof value === 'string') {
      switch (field.type) {
        case 'email':
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(value)) {
            error = 'Formato de email inválido';
          }
          break;
        case 'tel':
          const phoneRegex = /^\+?[\d\s\-\(\)]+$/;
          if (!phoneRegex.test(value)) {
            error = 'Formato de teléfono inválido';
          }
          break;
        case 'url':
          try {
            new URL(value);
          } catch {
            error = 'Formato de URL inválido';
          }
          break;
      }
    }
    
    setErrors(prev => ({ ...prev, [fieldName]: error || '' }));
  }, [fields, formData]);
  
  const validateForm = useCallback(() => {
    const newErrors: Record<string, string> = {};
    
    fields.forEach(field => {
      const value = formData[field.name];
      let error: string | null = null;
      
      // Required validation
      if (field.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
        error = `${field.label} es requerido`;
      }
      
      // Custom validation
      if (!error && field.validation && value) {
        error = field.validation(value);
      }
      
      if (error) {
        newErrors[field.name] = error;
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [fields, formData]);
  
  const handleFormSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setSubmitError(null);
    
    try {
      await onSubmit(formData);
      setSubmitSuccess(true);
      
      // Reset success state after 3 seconds
      setTimeout(() => setSubmitSuccess(false), 3000);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Error al enviar el formulario');
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, onSubmit, validateForm]);
  
  const progress = useMemo(() => {
    if (!showProgress) return 0;
    
    const completedFields = fields.filter(field => {
      const value = formData[field.name];
      return value !== undefined && value !== '' && value !== null;
    }).length;
    
    return Math.round((completedFields / fields.length) * 100);
  }, [formData, fields, showProgress]);
  
  const isFormValid = useMemo(() => {
    return Object.values(errors).every(error => !error) && 
           fields.filter(f => f.required).every(field => {
             const value = formData[field.name];
             return value !== undefined && value !== '' && value !== null;
           });
  }, [errors, fields, formData]);
  
  return (
    <FormContainer className={className} sx={sx}>
      {/* Header */}
      {(title || description) && (
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          {title && (
            <Typography variant="h4" component="h1" sx={{ mb: 2, fontWeight: 700 }}>
              {title}
            </Typography>
          )}
          {description && (
            <Typography variant="body1" color="text.secondary">
              {description}
            </Typography>
          )}
        </Box>
      )}
      
      {/* Progress Bar */}
      {showProgress && (
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Progreso del formulario
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {progress}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: alpha(theme.palette.primary.main, 0.1),
              '& .MuiLinearProgress-bar': {
                borderRadius: 4,
                background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
              },
            }}
          />
        </Box>
      )}
      
      {/* Form */}
      <Box component="form" onSubmit={handleFormSubmit} noValidate>
        {/* Fields */}
        {fields.map((field, index) => (
          <Grow
            key={field.name}
            in
            timeout={600}
            style={{ transitionDelay: `${index * 100}ms` }}
          >
            <div>
              <FieldRenderer
                field={field}
                value={formData[field.name]}
                error={touched[field.name] ? errors[field.name] : null}
                onChange={(value) => handleFieldChange(field.name, value)}
                onBlur={() => handleFieldBlur(field.name)}
              />
            </div>
          </Grow>
        ))}
        
        {/* Submit Error */}
        {submitError && (
          <Fade in>
            <Alert severity="error" sx={{ mb: 3 }}>
              {submitError}
            </Alert>
          </Fade>
        )}
        
        {/* Submit Success */}
        {submitSuccess && (
          <Fade in>
            <Alert severity="success" sx={{ mb: 3 }}>
              Formulario enviado exitosamente
            </Alert>
          </Fade>
        )}
        
        {/* Actions */}
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 4 }}>
          {onCancel && (
            <Button
              variant="outlined"
              onClick={onCancel}
              disabled={loading || isSubmitting}
              size="large"
            >
              {cancelLabel}
            </Button>
          )}
          
          <SubmitButton
            type="submit"
            variant="contained"
            disabled={loading || isSubmitting || disabled || !isFormValid}
            size="large"
          >
            {loading || isSubmitting ? 'Enviando...' : submitLabel}
          </SubmitButton>
        </Box>
      </Box>
    </FormContainer>
  );
});

EnhancedForm.displayName = 'EnhancedForm';

export default EnhancedForm; 