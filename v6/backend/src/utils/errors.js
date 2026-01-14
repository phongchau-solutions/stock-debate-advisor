/**
 * Custom error classes
 */

/**
 * Base API Error
 */
class ApiError extends Error {
  constructor(statusCode, message) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;

    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * Validation Error
 */
class ValidationError extends ApiError {
  constructor(message) {
    super(400, message);
    this.name = 'ValidationError';
  }
}

/**
 * Authentication Error
 */
class AuthenticationError extends ApiError {
  constructor(message = 'Authentication failed') {
    super(401, message);
    this.name = 'AuthenticationError';
  }
}

/**
 * Authorization Error
 */
class AuthorizationError extends ApiError {
  constructor(message = 'Access denied') {
    super(403, message);
    this.name = 'AuthorizationError';
  }
}

/**
 * Not Found Error
 */
class NotFoundError extends ApiError {
  constructor(message = 'Resource not found') {
    super(404, message);
    this.name = 'NotFoundError';
  }
}

/**
 * Conflict Error
 */
class ConflictError extends ApiError {
  constructor(message = 'Resource already exists') {
    super(409, message);
    this.name = 'ConflictError';
  }
}

/**
 * Service Error (for downstream service failures)
 */
class ServiceError extends ApiError {
  constructor(serviceName, message, originalError = null) {
    super(503, `${serviceName} error: ${message}`);
    this.name = 'ServiceError';
    this.serviceName = serviceName;
    this.originalError = originalError;
  }
}

/**
 * Timeout Error
 */
class TimeoutError extends ApiError {
  constructor(serviceName) {
    super(504, `${serviceName} request timed out`);
    this.name = 'TimeoutError';
    this.serviceName = serviceName;
  }
}

module.exports = {
  ApiError,
  ValidationError,
  AuthenticationError,
  AuthorizationError,
  NotFoundError,
  ConflictError,
  ServiceError,
  TimeoutError,
};
