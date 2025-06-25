#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 Analizando Bundle de SkyGuard Frontend...\n');

const buildDir = path.join(__dirname, '../build');
const staticDir = path.join(buildDir, 'static');

// Verificar que existe el build
if (!fs.existsSync(buildDir)) {
  console.error('❌ No se encontró la carpeta build. Ejecuta "npm run build" primero.');
  process.exit(1);
}

// Función para obtener el tamaño de archivo
function getFileSize(filePath) {
  const stats = fs.statSync(filePath);
  return Math.round(stats.size / 1024); // KB
}

// Función para obtener todos los archivos JS y CSS
function getBundleFiles() {
  const jsDir = path.join(staticDir, 'js');
  const cssDir = path.join(staticDir, 'css');
  
  const jsFiles = fs.existsSync(jsDir) ? fs.readdirSync(jsDir).filter(file => file.endsWith('.js')) : [];
  const cssFiles = fs.existsSync(cssDir) ? fs.readdirSync(cssDir).filter(file => file.endsWith('.css')) : [];
  
  return { jsFiles, cssFiles };
}

// Análisis principal
function analyzeBundles() {
  const { jsFiles, cssFiles } = getBundleFiles();
  
  let totalJSSize = 0;
  let totalCSSSize = 0;
  
  console.log('📦 Archivos JavaScript:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  jsFiles.forEach(file => {
    const filePath = path.join(staticDir, 'js', file);
    const size = getFileSize(filePath);
    totalJSSize += size;
    
    const status = size > 500 ? '🔴' : size > 300 ? '🟡' : '🟢';
    console.log(`${status} ${file.padEnd(40)} ${size.toString().padStart(6)} KB`);
  });
  
  console.log('\n📄 Archivos CSS:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  cssFiles.forEach(file => {
    const filePath = path.join(staticDir, 'css', file);
    const size = getFileSize(filePath);
    totalCSSSize += size;
    
    const status = size > 100 ? '🔴' : size > 50 ? '🟡' : '🟢';
    console.log(`${status} ${file.padEnd(40)} ${size.toString().padStart(6)} KB`);
  });
  
  const totalSize = totalJSSize + totalCSSSize;
  
  console.log('\n📊 Resumen del Bundle:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`📦 JavaScript Total:     ${totalJSSize.toString().padStart(6)} KB`);
  console.log(`🎨 CSS Total:            ${totalCSSSize.toString().padStart(6)} KB`);
  console.log(`📏 Tamaño Total:         ${totalSize.toString().padStart(6)} KB`);
  console.log(`📈 Tamaño Total (MB):    ${(totalSize / 1024).toFixed(2).padStart(6)} MB`);
  
  // Score de performance
  let score = 100;
  if (totalSize > 1000) score -= 40;
  else if (totalSize > 800) score -= 30;
  else if (totalSize > 600) score -= 20;
  else if (totalSize > 400) score -= 10;
  
  const mainJSFile = jsFiles.find(file => file.includes('main'));
  if (mainJSFile) {
    const mainSize = getFileSize(path.join(staticDir, 'js', mainJSFile));
    if (mainSize > 500) score -= 20;
    else if (mainSize > 300) score -= 10;
  }
  
  console.log(`\n🎯 Performance Score:    ${score}/100`);
  
  // Recomendaciones
  console.log('\n💡 Recomendaciones:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  if (totalSize > 600) {
    console.log('🔥 CRÍTICO: Bundle demasiado grande (>600KB)');
    console.log('   → Implementar code splitting más agresivo');
    console.log('   → Remover dependencias no utilizadas');
  }
  
  if (jsFiles.length < 3) {
    console.log('⚠️  Pocos chunks JS - considerar más code splitting');
  }
  
  const largeJSFiles = jsFiles.filter(file => {
    const filePath = path.join(staticDir, 'js', file);
    return getFileSize(filePath) > 300;
  });
  
  if (largeJSFiles.length > 0) {
    console.log('📦 Archivos JS grandes detectados:');
    largeJSFiles.forEach(file => {
      console.log(`   → ${file} - considerar splitting`);
    });
  }
  
  if (totalCSSSize > 50) {
    console.log('🎨 CSS grande - considerar purging de Tailwind/MUI');
  }
  
  console.log('\n🚀 Próximos pasos sugeridos:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('1. npm run build:analyze - Ver análisis visual');
  console.log('2. Implementar lazy loading más granular');
  console.log('3. Optimizar imports de MUI/Leaflet');
  console.log('4. Configurar webpack bundle splitting');
  
  return { totalSize, score };
}

// Ejecutar análisis
try {
  const { totalSize, score } = analyzeBundles();
  
  // Guardar métricas
  const metrics = {
    timestamp: new Date().toISOString(),
    totalSize,
    score,
    target: 600,
    status: totalSize <= 600 ? 'PASS' : 'FAIL'
  };
  
  fs.writeFileSync(
    path.join(__dirname, '../bundle-metrics.json'),
    JSON.stringify(metrics, null, 2)
  );
  
  console.log('\n✅ Análisis completado. Métricas guardadas en bundle-metrics.json');
  
  // Fallar si el bundle es demasiado grande
  if (totalSize > 800) {
    console.log('\n❌ Bundle size excede límite crítico (800KB)');
    process.exit(1);
  }
  
} catch (error) {
  console.error('❌ Error durante el análisis:', error.message);
  process.exit(1);
} 