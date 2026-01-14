/**
 * Main entry point for the backend service
 */

const createApp = require('./app');
const config = require('./config');
const logger = require('./utils/logger');

// Create Express app
const app = createApp();

// Start server
const server = app.listen(config.port, config.host, () => {
  logger.info(
    `Server started on http://${config.host}:${config.port} in ${config.nodeEnv} mode`
  );

  logger.info(`Data Service URL: ${config.services.dataService.url}`);
  logger.info(`AI Service URL: ${config.services.aiService.url}`);

  // Log available endpoints
  logger.info('Available endpoints:');
  logger.info('  Health: GET /health');
  logger.info('  Companies: GET /api/v1/companies/:symbol');
  logger.info('  Financials: GET /api/v1/financials/:symbol/quarterly');
  logger.info('  Debate: POST /api/v1/debate/start');
  logger.info('  Sessions: GET /api/v1/sessions');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  server.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error(`Uncaught exception: ${error.message}`);
  process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error(`Unhandled rejection at ${promise}: ${reason}`);
  process.exit(1);
});

module.exports = server;
