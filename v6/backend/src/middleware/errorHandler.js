/**
 * Error handling middleware
 */

const logger = require('../utils/logger');
const { ApiError } = require('../utils/errors');

/**
 * Global error handler middleware
 */
const errorHandler = (err, req, res, next) => {
  let error = err;

  // Log error
  logger.error(`Error: ${error.message}`, {
    path: req.path,
    method: req.method,
    statusCode: error.statusCode || 500,
    stack: error.stack,
  });

  // Default error object
  let status = error.statusCode || 500;
  let message = error.message || 'Internal Server Error';

  // Handle specific error types
  if (error.name === 'ValidationError') {
    status = 400;
  } else if (error.name === 'CastError') {
    status = 400;
    message = 'Invalid request';
  } else if (error.name === 'JsonWebTokenError') {
    status = 401;
    message = 'Invalid token';
  }

  // Send error response
  res.status(status).json({
    success: false,
    error: {
      status,
      message,
      ...(process.env.NODE_ENV === 'development' && { stack: error.stack }),
    },
  });
};

/**
 * Async error wrapper
 */
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

/**
 * 404 Not Found middleware
 */
const notFoundHandler = (req, res) => {
  res.status(404).json({
    success: false,
    error: {
      status: 404,
      message: 'Route not found',
      path: req.path,
    },
  });
};

module.exports = {
  errorHandler,
  asyncHandler,
  notFoundHandler,
};
