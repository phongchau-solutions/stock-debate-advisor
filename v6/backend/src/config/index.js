/**
 * Configuration management for backend service
 */

require('dotenv').config();

const config = {
  // Server Configuration
  nodeEnv: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '8000', 10),
  host: process.env.HOST || '0.0.0.0',

  // Service URLs
  services: {
    dataService: {
      url: process.env.DATA_SERVICE_URL || 'http://localhost:8001',
      timeout: parseInt(process.env.API_TIMEOUT || '30000', 10),
    },
    aiService: {
      url: process.env.AI_SERVICE_URL || 'http://localhost:8003',
      timeout: parseInt(process.env.API_TIMEOUT || '30000', 10),
    },
  },

  // Logging
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: process.env.LOG_FORMAT || 'json',
  },

  // API Configuration
  api: {
    timeout: parseInt(process.env.API_TIMEOUT || '30000', 10),
    enableCors: process.env.ENABLE_CORS !== 'false',
    corsOrigin: process.env.CORS_ORIGIN || 'http://localhost:3000',
  },

  // Authentication
  auth: {
    jwtSecret: process.env.JWT_SECRET || 'your-secret-key-change-in-production',
    jwtExpiry: process.env.JWT_EXPIRY || '24h',
    apiKeyPrefix: 'Bearer ',
  },

  // Rate Limiting
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000', 10),
    maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100', 10),
    perUser: process.env.RATE_LIMIT_PER_USER !== 'false',
  },

  // Security
  security: {
    enableValidation: process.env.ENABLE_VALIDATION !== 'false',
    enableLogging: process.env.ENABLE_LOGGING !== 'false',
    includeRequestInLogs: process.env.INCLUDE_REQUEST_IN_LOGS === 'true',
  },

  // Check if running in production
  isProduction() {
    return this.nodeEnv === 'production';
  },

  // Check if running in development
  isDevelopment() {
    return this.nodeEnv === 'development';
  },
};

module.exports = config;
