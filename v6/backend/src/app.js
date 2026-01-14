/**
 * Express application setup
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
require('express-async-errors');

const config = require('./config');
const logger = require('./utils/logger');
const { errorHandler, notFoundHandler } = require('./middleware/errorHandler');
const { httpLogger, logRequest } = require('./middleware/logger');

// Routes
const healthRoutes = require('./routes/health');
const authRoutes = require('./routes/auth');
const companiesRoutes = require('./routes/companies');
const financialsRoutes = require('./routes/financials');
const analysisRoutes = require('./routes/analysis');
const sessionRoutes = require('./routes/sessions');

/**
 * Create and configure Express application
 * @returns {express.Application} Configured Express app
 */
function createApp() {
  const app = express();

  // Security middleware
  app.use(helmet());

  // CORS middleware with restricted origin
  if (config.api.enableCors) {
    app.use(
      cors({
        origin: config.api.corsOrigin === '*' ? true : config.api.corsOrigin,
        credentials: true,
        methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        allowedHeaders: ['Content-Type', 'Authorization'],
      })
    );
  }

  // Compression middleware
  app.use(compression());

  // Request body parsing
  app.use(express.json({ limit: '50mb' }));
  app.use(express.urlencoded({ limit: '50mb', extended: true }));

  // Logging middleware
  app.use(httpLogger);
  app.use(logRequest);

  // API Routes
  app.use('/health', healthRoutes);
  app.use('/status', healthRoutes);
  app.use('/version', healthRoutes);

  // Authentication routes (no auth required)
  app.use('/api/v1/auth', authRoutes);

  // Data routes (with optional auth and rate limiting)
  app.use('/api/v1/companies', companiesRoutes);
  app.use('/api/v1/financials', financialsRoutes);
  app.use('/api/v1/prices', financialsRoutes);
  app.use('/api/v1/debate', analysisRoutes);
  app.use('/api/v1/sessions', sessionRoutes);

  // Root endpoint
  app.get('/', (req, res) => {
    res.json({
      service: 'Stock Debate Advisor Backend',
      version: '1.0.0',
      environment: config.nodeEnv,
      message: 'Welcome to Stock Debate Advisor API',
      security: {
        corsOrigin: config.api.corsOrigin,
        authentication: 'JWT (Bearer token)',
        rateLimit: 'Per user/IP',
      },
      endpoints: {
        health: '/health',
        version: '/version',
        status: '/status',
        auth: {
          login: 'POST /api/v1/auth/login',
          register: 'POST /api/v1/auth/register',
          verify: 'GET /api/v1/auth/verify',
          refresh: 'POST /api/v1/auth/refresh',
        },
        companies: '/api/v1/companies',
        financials: '/api/v1/financials',
        debate: '/api/v1/debate',
        sessions: '/api/v1/sessions',
      },
    });
  });

  // 404 handler
  app.use(notFoundHandler);

  // Error handler (must be last)
  app.use(errorHandler);

  return app;
}

module.exports = createApp;
