#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 Iniciando Auditoría de Rendimiento SkyGuard...\n');

class PerformanceAuditor {
  constructor() {
    this.results = {
      bundleSize: {},
      codeQuality: {},
      dependencies: {},
      performance: {},
      recommendations: []
    };
  }

  // 1. Análisis del Bundle Size
  async analyzeBundleSize() {
    console.log('📦 Analizando Bundle Size...');
    
    try {
      const buildPath = path.join(__dirname, '../build');
      const statsPath = path.join(buildPath, 'static');
      
      if (!fs.existsSync(buildPath)) {
        console.log('  ⚠️  Build no encontrado. Ejecutando build...');
        execSync('npm run build', { cwd: path.join(__dirname, '..') });
      }
      
      const getFileSize = (filePath) => {
        if (fs.existsSync(filePath)) {
          const stats = fs.statSync(filePath);
          return (stats.size / 1024).toFixed(2); // KB
        }
        return 0;
      };
      
      const jsFiles = fs.readdirSync(path.join(statsPath, 'js'))
        .filter(file => file.endsWith('.js'))
        .map(file => ({
          name: file,
          size: getFileSize(path.join(statsPath, 'js', file))
        }))
        .sort((a, b) => b.size - a.size);
      
      const cssFiles = fs.readdirSync(path.join(statsPath, 'css'))
        .filter(file => file.endsWith('.css'))
        .map(file => ({
          name: file,
          size: getFileSize(path.join(statsPath, 'css', file))
        }));
      
      const totalJS = jsFiles.reduce((sum, file) => sum + parseFloat(file.size), 0);
      const totalCSS = cssFiles.reduce((sum, file) => sum + parseFloat(file.size), 0);
      const totalSize = totalJS + totalCSS;
      
      this.results.bundleSize = {
        totalSize: totalSize.toFixed(2),
        jsSize: totalJS.toFixed(2),
        cssSize: totalCSS.toFixed(2),
        largestJS: jsFiles[0],
        jsFileCount: jsFiles.length,
        cssFileCount: cssFiles.length
      };
      
      console.log(`  📊 Tamaño total: ${totalSize.toFixed(2)} KB`);
      console.log(`  📄 JavaScript: ${totalJS.toFixed(2)} KB (${jsFiles.length} archivos)`);
      console.log(`  🎨 CSS: ${totalCSS.toFixed(2)} KB (${cssFiles.length} archivos)`);
      
      // Recomendaciones basadas en tamaño
      if (totalSize > 1000) {
        this.results.recommendations.push({
          type: 'bundle-size',
          severity: 'high',
          message: 'Bundle size excede 1MB. Considera code splitting y lazy loading.',
          action: 'Implementar lazy loading en rutas principales'
        });
      }
      
    } catch (error) {
      console.error('  ❌ Error analizando bundle:', error.message);
    }
  }

  // 2. Análisis de Dependencias
  async analyzeDependencies() {
    console.log('\n📚 Analizando Dependencias...');
    
    try {
      const packagePath = path.join(__dirname, '../package.json');
      const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
      
      const dependencies = packageData.dependencies || {};
      const devDependencies = packageData.devDependencies || {};
      
      const totalDeps = Object.keys(dependencies).length;
      const totalDevDeps = Object.keys(devDependencies).length;
      
      // Analizar dependencias pesadas conocidas
      const heavyDeps = [];
      const knownHeavy = {
        '@mui/material': 'Material-UI es pesado, considera tree shaking',
        'leaflet': 'Leaflet es necesario para mapas, pero verifica si usas todas las funciones',
        'moment': 'Moment.js es pesado, considera date-fns',
        'lodash': 'Lodash es pesado, importa funciones específicas',
        'chart.js': 'Chart.js puede ser pesado, considera alternatives ligeras'
      };
      
      Object.keys(dependencies).forEach(dep => {
        if (knownHeavy[dep]) {
          heavyDeps.push({ name: dep, reason: knownHeavy[dep] });
        }
      });
      
      this.results.dependencies = {
        totalDependencies: totalDeps,
        totalDevDependencies: totalDevDeps,
        heavyDependencies: heavyDeps
      };
      
      console.log(`  📦 Dependencias: ${totalDeps}`);
      console.log(`  🔧 Dev Dependencies: ${totalDevDeps}`);
      
      if (heavyDeps.length > 0) {
        console.log('  ⚠️  Dependencias pesadas detectadas:');
        heavyDeps.forEach(dep => {
          console.log(`    • ${dep.name}: ${dep.reason}`);
        });
      }
      
    } catch (error) {
      console.error('  ❌ Error analizando dependencias:', error.message);
    }
  }

  // 3. Análisis de Calidad de Código
  async analyzeCodeQuality() {
    console.log('\n🔍 Analizando Calidad de Código...');
    
    try {
      const srcPath = path.join(__dirname, '../src');
      const issues = {
        largeFiles: [],
        complexComponents: [],
        unusedImports: [],
        noKeyProps: []
      };
      
      const analyzeFile = (filePath) => {
        const content = fs.readFileSync(filePath, 'utf8');
        const lines = content.split('\n').length;
        const size = fs.statSync(filePath).size;
        
        // Archivos grandes (>300 líneas o >10KB)
        if (lines > 300 || size > 10240) {
          issues.largeFiles.push({
            file: path.relative(srcPath, filePath),
            lines,
            size: (size / 1024).toFixed(2) + ' KB'
          });
        }
        
        // Componentes complejos (muchos hooks/estados)
        const useStateCount = (content.match(/useState/g) || []).length;
        const useEffectCount = (content.match(/useEffect/g) || []).length;
        
        if (useStateCount > 5 || useEffectCount > 3) {
          issues.complexComponents.push({
            file: path.relative(srcPath, filePath),
            useState: useStateCount,
            useEffect: useEffectCount
          });
        }
        
        // Imports sin usar (básico)
        const imports = content.match(/^import\s+.*from\s+['"].*['"];?$/gm) || [];
        imports.forEach(importLine => {
          const match = importLine.match(/import\s+(?:{([^}]+)}|\*\s+as\s+(\w+)|(\w+))/);
          if (match) {
            const imported = match[1] || match[2] || match[3];
            if (imported && !content.includes(imported.trim())) {
              issues.unusedImports.push({
                file: path.relative(srcPath, filePath),
                import: importLine.trim()
              });
            }
          }
        });
      };
      
      const walkDir = (dir) => {
        const files = fs.readdirSync(dir);
        files.forEach(file => {
          const fullPath = path.join(dir, file);
          const stat = fs.statSync(fullPath);
          
          if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
            walkDir(fullPath);
          } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
            analyzeFile(fullPath);
          }
        });
      };
      
      walkDir(srcPath);
      
      this.results.codeQuality = issues;
      
      console.log(`  📄 Archivos grandes: ${issues.largeFiles.length}`);
      console.log(`  🔄 Componentes complejos: ${issues.complexComponents.length}`);
      console.log(`  🗑️  Imports sin usar: ${issues.unusedImports.length}`);
      
      // Recomendaciones
      if (issues.largeFiles.length > 0) {
        this.results.recommendations.push({
          type: 'code-quality',
          severity: 'medium',
          message: `${issues.largeFiles.length} archivos son muy grandes`,
          action: 'Considera dividir componentes grandes en sub-componentes'
        });
      }
      
    } catch (error) {
      console.error('  ❌ Error analizando código:', error.message);
    }
  }

  // 4. Generar Reporte
  generateReport() {
    console.log('\n📋 Generando Reporte de Auditoría...\n');
    
    const report = `
# 🔍 Reporte de Auditoría de Rendimiento - SkyGuard Frontend

## 📊 Resumen Ejecutivo
- **Bundle Size Total**: ${this.results.bundleSize.totalSize} KB
- **Archivos JavaScript**: ${this.results.bundleSize.jsFileCount} (${this.results.bundleSize.jsSize} KB)
- **Archivos CSS**: ${this.results.bundleSize.cssFileCount} (${this.results.bundleSize.cssSize} KB)
- **Dependencias**: ${this.results.dependencies.totalDependencies}
- **Problemas de Código**: ${(this.results.codeQuality.largeFiles || []).length + (this.results.codeQuality.complexComponents || []).length}

## 🎯 Recomendaciones Prioritarias

${this.results.recommendations.map(rec => `
### ${rec.severity === 'high' ? '🔴' : rec.severity === 'medium' ? '🟡' : '🟢'} ${rec.type.toUpperCase()}
**Problema**: ${rec.message}
**Acción**: ${rec.action}
`).join('')}

## 📦 Análisis Detallado del Bundle

### JavaScript Files
${this.results.bundleSize.largestJS ? `- **Archivo más grande**: ${this.results.bundleSize.largestJS.name} (${this.results.bundleSize.largestJS.size} KB)` : ''}

### Dependencias Pesadas
${(this.results.dependencies.heavyDependencies || []).map(dep => `
- **${dep.name}**: ${dep.reason}`).join('')}

## 🔧 Problemas de Calidad de Código

### Archivos Grandes (>300 líneas)
${(this.results.codeQuality.largeFiles || []).map(file => `
- **${file.file}**: ${file.lines} líneas (${file.size})`).join('')}

### Componentes Complejos
${(this.results.codeQuality.complexComponents || []).map(comp => `
- **${comp.file}**: ${comp.useState} useState, ${comp.useEffect} useEffect`).join('')}

## 💡 Próximos Pasos

1. **Inmediato** (0-1 semana):
   - Ejecutar script de optimización de imports: \`npm run optimize:imports\`
   - Implementar lazy loading en rutas principales
   - Optimizar imports de Material-UI

2. **Corto Plazo** (1-2 semanas):
   - Refactorizar componentes complejos
   - Implementar code splitting
   - Optimizar imágenes y assets

3. **Mediano Plazo** (2-4 semanas):
   - Migrar a alternativas más ligeras de dependencias pesadas
   - Implementar service workers para cache
   - Optimizar bundle chunks

---
*Reporte generado el ${new Date().toLocaleString()}*
    `;
    
    const reportPath = path.join(__dirname, '../performance-audit-report.md');
    fs.writeFileSync(reportPath, report.trim(), 'utf8');
    
    console.log('✅ Reporte guardado en: performance-audit-report.md');
    console.log('\n🚀 Para mejorar el rendimiento, ejecuta:');
    console.log('  npm run optimize:imports');
    console.log('  npm run build:analyze');
    console.log('  npm run build -- --profile');
  }

  // Ejecutar auditoría completa
  async runAudit() {
    try {
      await this.analyzeBundleSize();
      await this.analyzeDependencies();
      await this.analyzeCodeQuality();
      this.generateReport();
      
      console.log('\n✨ Auditoría completada exitosamente!');
    } catch (error) {
      console.error('\n❌ Error durante la auditoría:', error.message);
    }
  }
}

// Ejecutar auditoría
const auditor = new PerformanceAuditor();
auditor.runAudit(); 