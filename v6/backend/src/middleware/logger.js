/**
 * HTTP request logging middleware
 */

const morgan = require('morgan');
const logger = require('../utils/logger');

// Create morgan middleware with custom tokens
const httpLogger = morgan((tokens, req, res) => {
  return JSON.stringify({
    timestamp: new Date().toISOString(),
    method: tokens.method(req, res),
    url: tokens.url(req, res),
    status: tokens.status(req, res),
    responseTime: `${tokens['response-time'](req, res)}ms`,
    contentLength: tokens.res(req, res, 'content-length'),
    userAgent: req.get('user-agent'),
  });
});

// Custom logger for important events
const logRequest = (req, res, next) => {
  const startTime = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - startTime;
    const level =
      res.statusCode >= 400 ? 'warn' : res.statusCode >= 500 ? 'error' : 'info';

    logger.log(
      level,
      `${req.method} ${req.path} - ${res.statusCode} (${duration}ms)`
    );
  });

  next();
};

module.exports = {
  httpLogger,
  logRequest,
};
