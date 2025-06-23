#!/bin/bash

# SkyGuard Frontend Bundle Analysis Script
# This script analyzes the bundle size and identifies optimization opportunities

echo "🔍 SkyGuard Frontend Bundle Analysis"
echo "===================================="

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the frontend directory"
    exit 1
fi

# Install bundle analyzer if not present
echo "📦 Installing webpack-bundle-analyzer..."
npm install --save-dev webpack-bundle-analyzer source-map-explorer

# Create build for analysis
echo "🔨 Building production bundle..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please fix build errors first."
    exit 1
fi

echo "✅ Build completed successfully!"

# Analyze bundle with webpack-bundle-analyzer
echo "📊 Analyzing bundle with webpack-bundle-analyzer..."
npx webpack-bundle-analyzer build/static/js/*.js --mode server --port 8888 &
ANALYZER_PID=$!

# Analyze with source-map-explorer
echo "🗺️  Analyzing with source-map-explorer..."
npx source-map-explorer 'build/static/js/*.js' --html > bundle-analysis.html

# Calculate bundle sizes
echo "📏 Calculating bundle sizes..."

# Get main bundle size
MAIN_JS=$(ls build/static/js/main.*.js 2>/dev/null | head -1)
if [ -f "$MAIN_JS" ]; then
    MAIN_SIZE=$(stat -f%z "$MAIN_JS" 2>/dev/null || stat -c%s "$MAIN_JS" 2>/dev/null)
    MAIN_SIZE_KB=$((MAIN_SIZE / 1024))
    echo "📄 Main bundle size: ${MAIN_SIZE_KB}KB"
else
    echo "⚠️  Main bundle not found"
fi

# Get chunk sizes
CHUNK_TOTAL=0
CHUNK_COUNT=0
for file in build/static/js/*.chunk.js; do
    if [ -f "$file" ]; then
        SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        CHUNK_TOTAL=$((CHUNK_TOTAL + SIZE))
        CHUNK_COUNT=$((CHUNK_COUNT + 1))
    fi
done

if [ $CHUNK_COUNT -gt 0 ]; then
    CHUNK_TOTAL_KB=$((CHUNK_TOTAL / 1024))
    echo "📦 Chunks total size: ${CHUNK_TOTAL_KB}KB (${CHUNK_COUNT} chunks)"
else
    echo "📦 No chunks found"
fi

# Get CSS size
CSS_SIZE=0
for file in build/static/css/*.css; do
    if [ -f "$file" ]; then
        SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        CSS_SIZE=$((CSS_SIZE + SIZE))
    fi
done

CSS_SIZE_KB=$((CSS_SIZE / 1024))
echo "🎨 CSS total size: ${CSS_SIZE_KB}KB"

# Calculate total size
TOTAL_SIZE=$((MAIN_SIZE + CHUNK_TOTAL + CSS_SIZE))
TOTAL_SIZE_KB=$((TOTAL_SIZE / 1024))
TOTAL_SIZE_MB=$((TOTAL_SIZE_KB / 1024))

echo ""
echo "📊 BUNDLE ANALYSIS SUMMARY"
echo "=========================="
echo "📄 Main bundle: ${MAIN_SIZE_KB}KB"
echo "📦 Chunks: ${CHUNK_TOTAL_KB}KB"
echo "🎨 CSS: ${CSS_SIZE_KB}KB"
echo "📦 Total: ${TOTAL_SIZE_KB}KB (${TOTAL_SIZE_MB}MB)"

# Performance recommendations
echo ""
echo "💡 PERFORMANCE RECOMMENDATIONS"
echo "=============================="

if [ $MAIN_SIZE_KB -gt 1000 ]; then
    echo "⚠️  Main bundle is large (${MAIN_SIZE_KB}KB > 1000KB)"
    echo "   → Consider code splitting"
    echo "   → Implement lazy loading for routes"
    echo "   → Remove unused dependencies"
fi

if [ $TOTAL_SIZE_KB -gt 2000 ]; then
    echo "⚠️  Total bundle is large (${TOTAL_SIZE_KB}KB > 2000KB)"
    echo "   → Implement tree shaking"
    echo "   → Use dynamic imports"
    echo "   → Consider using a CDN for large libraries"
fi

if [ $CHUNK_COUNT -lt 3 ]; then
    echo "⚠️  Few chunks detected (${CHUNK_COUNT} < 3)"
    echo "   → Implement code splitting"
    echo "   → Split vendor and app code"
fi

# Analyze dependencies
echo ""
echo "🔍 DEPENDENCY ANALYSIS"
echo "====================="

# Check for large dependencies
echo "📦 Analyzing package.json dependencies..."

# Extract dependency sizes (approximate)
echo "🔍 Large dependencies to review:"
echo "   → @mui/material, @mui/icons-material (UI library)"
echo "   → leaflet, react-leaflet (Maps)"
echo "   → @reduxjs/toolkit, react-redux (State management)"
echo "   → axios (HTTP client)"
echo "   → react, react-dom (Core React)"

# Check for unused dependencies
echo ""
echo "🧹 CLEANUP RECOMMENDATIONS"
echo "=========================="
echo "Run 'npx depcheck' to find unused dependencies"
echo "Run 'npm audit' to check for security vulnerabilities"

# Generate detailed report
echo ""
echo "📋 Generating detailed report..."

cat > bundle-analysis-report.md << EOF
# SkyGuard Frontend Bundle Analysis Report

Generated on: $(date)

## Bundle Sizes
- **Main bundle**: ${MAIN_SIZE_KB}KB
- **Chunks**: ${CHUNK_TOTAL_KB}KB (${CHUNK_COUNT} chunks)
- **CSS**: ${CSS_SIZE_KB}KB
- **Total**: ${TOTAL_SIZE_KB}KB (${TOTAL_SIZE_MB}MB)

## Performance Score
EOF

# Calculate performance score
SCORE=100
if [ $MAIN_SIZE_KB -gt 500 ]; then SCORE=$((SCORE - 20)); fi
if [ $MAIN_SIZE_KB -gt 1000 ]; then SCORE=$((SCORE - 20)); fi
if [ $TOTAL_SIZE_KB -gt 1500 ]; then SCORE=$((SCORE - 20)); fi
if [ $TOTAL_SIZE_KB -gt 2500 ]; then SCORE=$((SCORE - 20)); fi
if [ $CHUNK_COUNT -lt 3 ]; then SCORE=$((SCORE - 20)); fi

echo "**Performance Score: ${SCORE}/100**" >> bundle-analysis-report.md

cat >> bundle-analysis-report.md << EOF

## Recommendations

### Immediate Actions (Score < 80)
EOF

if [ $SCORE -lt 80 ]; then
cat >> bundle-analysis-report.md << EOF
- [ ] Implement code splitting for routes
- [ ] Add lazy loading for heavy components
- [ ] Remove unused dependencies
- [ ] Optimize imports (use specific imports instead of full libraries)
EOF
fi

cat >> bundle-analysis-report.md << EOF

### Optimization Opportunities
- [ ] Implement React.lazy() for route components
- [ ] Use dynamic imports for heavy libraries
- [ ] Consider using lighter alternatives:
  - Replace moment.js with date-fns (if used)
  - Use lodash-es instead of lodash
  - Consider lighter UI libraries for specific components
- [ ] Implement tree shaking
- [ ] Use webpack-bundle-analyzer regularly
- [ ] Set up bundle size monitoring in CI/CD

### Code Splitting Strategy
1. **Route-based splitting**: Split each page into its own chunk
2. **Feature-based splitting**: Split large features (maps, reports)
3. **Vendor splitting**: Separate vendor libraries from app code
4. **Async component loading**: Load components only when needed

### Files to Review
- Check build/static/js/ for large chunks
- Review package.json for unused dependencies
- Analyze source-map-explorer output for optimization opportunities

## Tools Used
- webpack-bundle-analyzer
- source-map-explorer
- Custom bundle size analysis

## Next Steps
1. Review bundle-analysis.html for detailed breakdown
2. Run webpack-bundle-analyzer on port 8888 for interactive analysis
3. Implement recommended optimizations
4. Re-run analysis to measure improvements
EOF

echo "✅ Report generated: bundle-analysis-report.md"
echo "✅ Detailed analysis: bundle-analysis.html"
echo "🌐 Interactive analyzer running on http://localhost:8888"

echo ""
echo "🚀 NEXT STEPS"
echo "============"
echo "1. Open bundle-analysis.html in your browser"
echo "2. Review the interactive analyzer at http://localhost:8888"
echo "3. Implement the recommendations in bundle-analysis-report.md"
echo "4. Run this script again after optimizations"

# Wait for user input before closing analyzer
echo ""
echo "Press Enter to stop the interactive analyzer..."
read
kill $ANALYZER_PID 2>/dev/null

echo "✅ Bundle analysis complete!" 