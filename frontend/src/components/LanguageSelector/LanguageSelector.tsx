import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
  Box,
  Typography,
} from '@mui/material';
import { Language as LanguageIcon } from '@mui/icons-material';
import { useLanguage } from '../../hooks/useLanguage';

interface LanguageSelectorProps {
  variant?: 'standard' | 'outlined' | 'filled';
  size?: 'small' | 'medium';
  fullWidth?: boolean;
  showLabel?: boolean;
  sx?: object;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  variant = 'outlined',
  size = 'medium',
  fullWidth = true,
  showLabel = true,
  sx = {},
}) => {
  const { changeLanguage, getCurrentLanguage, getAvailableLanguages, t } = useLanguage();

  const handleLanguageChange = (event: any) => {
    changeLanguage(event.target.value);
  };

  const languages = getAvailableLanguages();
  const currentLanguage = getCurrentLanguage();

  return (
    <FormControl variant={variant} size={size} fullWidth={fullWidth} sx={sx}>
      {showLabel && (
        <InputLabel id="language-selector-label">
          {t('configuration.language')}
        </InputLabel>
      )}
      <Select
        labelId="language-selector-label"
        id="language-selector"
        value={currentLanguage}
        label={showLabel ? t('configuration.language') : undefined}
        onChange={handleLanguageChange}
        startAdornment={
          <InputAdornment position="start">
            <LanguageIcon color="action" />
          </InputAdornment>
        }
        sx={{ 
          '& .MuiOutlinedInput-root': { borderRadius: 2 },
          ...sx 
        }}
      >
        {languages.map((language) => (
          <MenuItem key={language.code} value={language.code}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography>{language.name}</Typography>
            </Box>
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default LanguageSelector; 