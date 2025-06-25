// Performance Analysis Script for SkyGuard Frontend
// This script helps identify performance bottlenecks in React components

class PerformanceAnalyzer {
  constructor() {
    this.componentMetrics = new Map();
    this.apiMetrics = new Map();
    this.renderTimes = [];
    this.memoryUsage = [];
    this.isAnalyzing = false;
  }

  // Start performance monitoring
  startAnalysis() {
    if (this.isAnalyzing) return;
    
    console.log('🚀 Starting Performance Analysis...');
    this.isAnalyzing = true;
    
    // Monitor component renders
    this.monitorComponentRenders();
    
    // Monitor API calls
    this.monitorAPIRequests();
    
    // Monitor memory usage
    this.monitorMemoryUsage();
    
    // Monitor navigation timing
    this.monitorNavigationTiming();
    
    // Set up periodic reporting
    this.reportInterval = setInterval(() => {
      this.generateReport();
    }, 30000); // Report every 30 seconds
  }

  // Stop performance monitoring
  stopAnalysis() {
    if (!this.isAnalyzing) return;
    
    console.log('🛑 Stopping Performance Analysis...');
    this.isAnalyzing = false;
    
    if (this.reportInterval) {
      clearInterval(this.reportInterval);
    }
    
    // Generate final report
    this.generateFinalReport();
  }

  // Monitor component render times using Performance Observer
  monitorComponentRenders() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.name.includes('React')) {
            this.recordComponentMetric(entry.name, entry.duration);
          }
        });
      });
      
      observer.observe({ entryTypes: ['measure'] });
    }
  }

  // Monitor API request performance
  monitorAPIRequests() {
    const originalFetch = window.fetch;
    const analyzer = this;
    
    window.fetch = function(...args) {
      const startTime = performance.now();
      const url = args[0];
      
      return originalFetch.apply(this, args)
        .then(response => {
          const endTime = performance.now();
          const duration = endTime - startTime;
          
          analyzer.recordAPIMetric(url, duration, response.status);
          
          return response;
        })
        .catch(error => {
          const endTime = performance.now();
          const duration = endTime - startTime;
          
          analyzer.recordAPIMetric(url, duration, 'ERROR');
          
          throw error;
        });
    };
  }

  // Monitor memory usage
  monitorMemoryUsage() {
    if ('memory' in performance) {
      setInterval(() => {
        const memory = performance.memory;
        this.memoryUsage.push({
          timestamp: Date.now(),
          usedJSHeapSize: memory.usedJSHeapSize,
          totalJSHeapSize: memory.totalJSHeapSize,
          jsHeapSizeLimit: memory.jsHeapSizeLimit
        });
        
        // Keep only last 100 measurements
        if (this.memoryUsage.length > 100) {
          this.memoryUsage.shift();
        }
      }, 5000); // Every 5 seconds
    }
  }

  // Monitor navigation timing
  monitorNavigationTiming() {
    if ('navigation' in performance) {
      const nav = performance.getEntriesByType('navigation')[0];
      
      console.log('📊 Navigation Timing:', {
        domContentLoaded: nav.domContentLoadedEventEnd - nav.domContentLoadedEventStart,
        loadComplete: nav.loadEventEnd - nav.loadEventStart,
        totalPageLoad: nav.loadEventEnd - nav.fetchStart
      });
    }
  }

  // Record component performance metric
  recordComponentMetric(componentName, duration) {
    if (!this.componentMetrics.has(componentName)) {
      this.componentMetrics.set(componentName, {
        count: 0,
        totalTime: 0,
        maxTime: 0,
        minTime: Infinity,
        averageTime: 0
      });
    }
    
    const metric = this.componentMetrics.get(componentName);
    metric.count++;
    metric.totalTime += duration;
    metric.maxTime = Math.max(metric.maxTime, duration);
    metric.minTime = Math.min(metric.minTime, duration);
    metric.averageTime = metric.totalTime / metric.count;
    
    // Log slow renders
    if (duration > 16) { // More than one frame (60fps)
      console.warn(`🐌 Slow render detected: ${componentName} took ${duration.toFixed(2)}ms`);
    }
  }

  // Record API performance metric
  recordAPIMetric(url, duration, status) {
    const endpoint = this.extractEndpoint(url);
    
    if (!this.apiMetrics.has(endpoint)) {
      this.apiMetrics.set(endpoint, {
        count: 0,
        totalTime: 0,
        maxTime: 0,
        minTime: Infinity,
        averageTime: 0,
        errors: 0,
        statusCodes: {}
      });
    }
    
    const metric = this.apiMetrics.get(endpoint);
    metric.count++;
    metric.totalTime += duration;
    metric.maxTime = Math.max(metric.maxTime, duration);
    metric.minTime = Math.min(metric.minTime, duration);
    metric.averageTime = metric.totalTime / metric.count;
    
    if (status === 'ERROR' || status >= 400) {
      metric.errors++;
    }
    
    metric.statusCodes[status] = (metric.statusCodes[status] || 0) + 1;
    
    // Log slow API calls
    if (duration > 1000) { // More than 1 second
      console.warn(`🐌 Slow API call: ${endpoint} took ${duration.toFixed(2)}ms`);
    }
  }

  // Extract endpoint from URL
  extractEndpoint(url) {
    try {
      const urlObj = new URL(url, window.location.origin);
      return urlObj.pathname.replace(/\/\d+/g, '/:id'); // Replace IDs with :id
    } catch {
      return url;
    }
  }

  // Generate periodic report
  generateReport() {
    console.group('📊 Performance Report');
    
    // Component performance
    console.group('🧩 Component Performance');
    const sortedComponents = Array.from(this.componentMetrics.entries())
      .sort((a, b) => b[1].averageTime - a[1].averageTime)
      .slice(0, 10);
      
    sortedComponents.forEach(([name, metric]) => {
      console.log(`${name}: ${metric.averageTime.toFixed(2)}ms avg (${metric.count} renders)`);
    });
    console.groupEnd();
    
    // API performance
    console.group('🌐 API Performance');
    const sortedAPIs = Array.from(this.apiMetrics.entries())
      .sort((a, b) => b[1].averageTime - a[1].averageTime)
      .slice(0, 10);
      
    sortedAPIs.forEach(([endpoint, metric]) => {
      console.log(`${endpoint}: ${metric.averageTime.toFixed(2)}ms avg (${metric.count} calls, ${metric.errors} errors)`);
    });
    console.groupEnd();
    
    // Memory usage
    if (this.memoryUsage.length > 0) {
      const latest = this.memoryUsage[this.memoryUsage.length - 1];
      console.log(`💾 Memory Usage: ${(latest.usedJSHeapSize / 1024 / 1024).toFixed(2)}MB`);
    }
    
    console.groupEnd();
  }

  // Generate final comprehensive report
  generateFinalReport() {
    console.group('📋 Final Performance Analysis Report');
    
    // Summary statistics
    const totalComponents = this.componentMetrics.size;
    const totalAPICalls = Array.from(this.apiMetrics.values())
      .reduce((sum, metric) => sum + metric.count, 0);
    
    console.log(`📊 Summary:`);
    console.log(`- Components analyzed: ${totalComponents}`);
    console.log(`- API calls monitored: ${totalAPICalls}`);
    console.log(`- Analysis duration: ${Date.now() - this.startTime}ms`);
    
    // Performance issues detected
    console.group('⚠️ Performance Issues');
    
    // Slow components
    const slowComponents = Array.from(this.componentMetrics.entries())
      .filter(([name, metric]) => metric.averageTime > 16)
      .sort((a, b) => b[1].averageTime - a[1].averageTime);
      
    if (slowComponents.length > 0) {
      console.warn('🐌 Slow Components (>16ms):');
      slowComponents.forEach(([name, metric]) => {
        console.warn(`  - ${name}: ${metric.averageTime.toFixed(2)}ms avg`);
      });
    }
    
    // Slow APIs
    const slowAPIs = Array.from(this.apiMetrics.entries())
      .filter(([endpoint, metric]) => metric.averageTime > 500)
      .sort((a, b) => b[1].averageTime - a[1].averageTime);
      
    if (slowAPIs.length > 0) {
      console.warn('🐌 Slow API Endpoints (>500ms):');
      slowAPIs.forEach(([endpoint, metric]) => {
        console.warn(`  - ${endpoint}: ${metric.averageTime.toFixed(2)}ms avg`);
      });
    }
    
    // Memory leaks
    if (this.memoryUsage.length > 10) {
      const first = this.memoryUsage[0];
      const last = this.memoryUsage[this.memoryUsage.length - 1];
      const memoryGrowth = last.usedJSHeapSize - first.usedJSHeapSize;
      
      if (memoryGrowth > 10 * 1024 * 1024) { // 10MB growth
        console.warn(`💾 Potential memory leak detected: ${(memoryGrowth / 1024 / 1024).toFixed(2)}MB growth`);
      }
    }
    
    console.groupEnd();
    
    // Recommendations
    console.group('💡 Recommendations');
    
    if (slowComponents.length > 0) {
      console.log('🧩 Component Optimization:');
      console.log('  - Add React.memo() to slow components');
      console.log('  - Use useMemo() for expensive calculations');
      console.log('  - Use useCallback() for event handlers');
    }
    
    if (slowAPIs.length > 0) {
      console.log('🌐 API Optimization:');
      console.log('  - Implement request caching');
      console.log('  - Reduce polling frequency');
      console.log('  - Use pagination for large datasets');
    }
    
    console.log('🚀 General Optimizations:');
    console.log('  - Implement code splitting');
    console.log('  - Add virtual scrolling for long lists');
    console.log('  - Optimize bundle size');
    
    console.groupEnd();
    console.groupEnd();
    
    // Export data for further analysis
    return {
      components: Object.fromEntries(this.componentMetrics),
      apis: Object.fromEntries(this.apiMetrics),
      memory: this.memoryUsage
    };
  }

  // Get current performance snapshot
  getSnapshot() {
    return {
      timestamp: Date.now(),
      components: Object.fromEntries(this.componentMetrics),
      apis: Object.fromEntries(this.apiMetrics),
      memory: this.memoryUsage.length > 0 ? this.memoryUsage[this.memoryUsage.length - 1] : null
    };
  }
}

// Create global instance
window.performanceAnalyzer = new PerformanceAnalyzer();

// Auto-start in development
if (process.env.NODE_ENV === 'development') {
  console.log('🔍 Performance Analyzer ready! Use:');
  console.log('  - window.performanceAnalyzer.startAnalysis() to start');
  console.log('  - window.performanceAnalyzer.stopAnalysis() to stop');
  console.log('  - window.performanceAnalyzer.generateReport() for current report');
}

export default window.performanceAnalyzer; 