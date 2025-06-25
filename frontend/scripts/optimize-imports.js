#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

console.log('🔧 Optimizando imports de Material-UI para mejor tree shaking...\n');

// Patrones para detectar imports de MUI que se pueden optimizar
const MUI_PATTERNS = {
  // import { Button, TextField } from '@mui/material';
  BULK_MATERIAL: /import\s*{\s*([^}]+)\s*}\s*from\s*['"]@mui\/material['"];?/g,
  
  // import { Add, Delete } from '@mui/icons-material';
  BULK_ICONS: /import\s*{\s*([^}]+)\s*}\s*from\s*['"]@mui\/icons-material['"];?/g,
};

// Función para optimizar un archivo
function optimizeFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let hasChanges = false;
  
  // Optimizar imports de @mui/material
  content = content.replace(MUI_PATTERNS.BULK_MATERIAL, (match, imports) => {
    hasChanges = true;
    const importList = imports
      .split(',')
      .map(imp => imp.trim())
      .filter(imp => imp.length > 0);
    
    const optimizedImports = importList
      .map(imp => `import ${imp} from '@mui/material/${imp}';`)
      .join('\n');
    
    console.log(`  📦 Optimizando ${importList.length} imports de Material-UI en ${path.basename(filePath)}`);
    return optimizedImports;
  });
  
  // Optimizar imports de @mui/icons-material
  content = content.replace(MUI_PATTERNS.BULK_ICONS, (match, imports) => {
    hasChanges = true;
    const importList = imports
      .split(',')
      .map(imp => imp.trim())
      .filter(imp => imp.length > 0);
    
    const optimizedImports = importList
      .map(imp => `import ${imp} from '@mui/icons-material/${imp}';`)
      .join('\n');
    
    console.log(`  🎨 Optimizando ${importList.length} imports de iconos en ${path.basename(filePath)}`);
    return optimizedImports;
  });
  
  if (hasChanges) {
    fs.writeFileSync(filePath, content, 'utf8');
    return true;
  }
  
  return false;
}

// Función principal
function optimizeImports() {
  const srcPath = path.join(__dirname, '../src');
  const pattern = path.join(srcPath, '**/*.{ts,tsx}');
  
  console.log(`🔍 Buscando archivos en: ${srcPath}`);
  
  const files = glob.sync(pattern, {
    ignore: [
      '**/node_modules/**',
      '**/build/**',
      '**/*.test.{ts,tsx}',
      '**/*.spec.{ts,tsx}',
    ],
  });
  
  console.log(`📁 Encontrados ${files.length} archivos para analizar\n`);
  
  let optimizedFiles = 0;
  let totalImportsOptimized = 0;
  
  files.forEach(file => {
    const relativePath = path.relative(srcPath, file);
    
    try {
      const wasOptimized = optimizeFile(file);
      if (wasOptimized) {
        optimizedFiles++;
        console.log(`  ✅ ${relativePath}`);
      }
    } catch (error) {
      console.error(`  ❌ Error procesando ${relativePath}:`, error.message);
    }
  });
  
  console.log('\n📊 Resumen de Optimización:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`📁 Archivos analizados:    ${files.length}`);
  console.log(`✨ Archivos optimizados:   ${optimizedFiles}`);
  console.log(`📦 Reducción estimada:     ~${(optimizedFiles * 15).toFixed(0)}KB`);
  
  if (optimizedFiles > 0) {
    console.log('\n🚀 Beneficios de la optimización:');
    console.log('  • Mejor tree shaking');
    console.log('  • Bundle size más pequeño');
    console.log('  • Tiempos de carga más rápidos');
    console.log('  • Imports más específicos');
    
    console.log('\n💡 Próximos pasos:');
    console.log('  1. npm run build - Verificar el nuevo bundle size');
    console.log('  2. npm run build:analyze - Analizar mejoras');
    console.log('  3. npm test - Verificar que todo funcione');
  } else {
    console.log('\n✅ Todos los imports ya están optimizados!');
  }
}

// Función para verificar dependencias necesarias
function checkDependencies() {
  try {
    require('glob');
    return true;
  } catch (error) {
    console.error('❌ Dependencia faltante: glob');
    console.log('💡 Instala con: npm install --save-dev glob');
    return false;
  }
}

// Ejecutar optimización
if (checkDependencies()) {
  optimizeImports();
} else {
  process.exit(1);
} 