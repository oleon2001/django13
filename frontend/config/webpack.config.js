const path = require('path');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = function(webpackEnv) {
  const isEnvDevelopment = webpackEnv === 'development';
  const isEnvProduction = webpackEnv === 'production';

  return {
    mode: isEnvProduction ? 'production' : isEnvDevelopment && 'development',
    
    // Enhanced optimization for production
    optimization: {
      minimize: isEnvProduction,
      sideEffects: false, // Enable aggressive tree shaking
      usedExports: true,
      
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          // Vendor chunk for stable libraries
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 10,
            reuseExistingChunk: true,
          },
          
          // MUI chunk (large library)
          mui: {
            test: /[\\/]node_modules[\\/]@mui[\\/]/,
            name: 'mui',
            chunks: 'all',
            priority: 20,
            reuseExistingChunk: true,
          },
          
          // Leaflet chunk (map library)
          leaflet: {
            test: /[\\/]node_modules[\\/]leaflet[\\/]|[\\/]react-leaflet[\\/]/,
            name: 'leaflet',
            chunks: 'all',
            priority: 15,
            reuseExistingChunk: true,
          },
          
          // Common components chunk
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            priority: 5,
            reuseExistingChunk: true,
          },
        },
      },
    },

    resolve: {
      alias: {
        '@': path.resolve(__dirname, '../src'),
        '@components': path.resolve(__dirname, '../src/components'),
        '@pages': path.resolve(__dirname, '../src/pages'),
        '@services': path.resolve(__dirname, '../src/services'),
        '@hooks': path.resolve(__dirname, '../src/hooks'),
        '@utils': path.resolve(__dirname, '../src/utils'),
        '@types': path.resolve(__dirname, '../src/types'),
      },
      extensions: ['.ts', '.tsx', '.js', '.jsx'],
    },

    module: {
      rules: [
        // TypeScript/JavaScript processing
        {
          test: /\.(ts|tsx|js|jsx)$/,
          exclude: /node_modules/,
          use: [
            {
              loader: 'babel-loader',
              options: {
                presets: [
                  ['@babel/preset-env', { useBuiltIns: 'entry', corejs: 3 }],
                  '@babel/preset-react',
                  '@babel/preset-typescript',
                ],
                plugins: [
                  // Tree shaking for MUI
                  ['babel-plugin-import', {
                    libraryName: '@mui/material',
                    libraryDirectory: '',
                    camel2DashComponentName: false,
                  }, 'core'],
                  ['babel-plugin-import', {
                    libraryName: '@mui/icons-material',
                    libraryDirectory: '',
                    camel2DashComponentName: false,
                  }, 'icons'],
                  
                  // Other optimizations
                  '@babel/plugin-proposal-class-properties',
                  '@babel/plugin-syntax-dynamic-import',
                ],
              },
            },
          ],
        },
        
        // CSS processing
        {
          test: /\.css$/,
          use: [
            'style-loader',
            {
              loader: 'css-loader',
              options: {
                importLoaders: 1,
                modules: {
                  auto: true,
                  localIdentName: isEnvDevelopment 
                    ? '[name]__[local]--[hash:base64:5]' 
                    : '[hash:base64:8]',
                },
              },
            },
            'postcss-loader',
          ],
        },
      ],
    },

    plugins: [
      // Bundle analyzer for development
      ...(isEnvDevelopment ? [
        new BundleAnalyzerPlugin({
          analyzerMode: 'server',
          openAnalyzer: false,
          analyzerHost: 'localhost',
          analyzerPort: 8888,
        }),
      ] : []),
      
      // Bundle analyzer for production (generate static report)
      ...(isEnvProduction ? [
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          reportFilename: '../bundle-analysis.html',
          openAnalyzer: false,
        }),
      ] : []),
    ],

    // Performance hints
    performance: {
      hints: isEnvProduction ? 'warning' : false,
      maxEntrypointSize: 600000, // 600KB
      maxAssetSize: 600000, // 600KB
    },

    // Development server optimizations
    devServer: isEnvDevelopment ? {
      compress: true,
      hot: true,
      open: false,
      overlay: {
        warnings: false,
        errors: true,
      },
    } : undefined,
  };
}; 