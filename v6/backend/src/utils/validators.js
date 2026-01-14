/**
 * Validation utilities
 */

const validator = require('validator');
const { ValidationError } = require('./errors');

/**
 * Validate stock symbol (e.g., MBB, VCB, FPT)
 * @param {string} symbol - Stock symbol to validate
 * @throws {ValidationError} If symbol is invalid
 * @returns {string} Validated symbol
 */
function validateSymbol(symbol) {
  if (!symbol || typeof symbol !== 'string') {
    throw new ValidationError('Symbol is required and must be a string');
  }

  const trimmedSymbol = symbol.trim().toUpperCase();

  // Stock symbol pattern: 1-10 alphanumeric characters
  if (!/^[A-Z0-9]{1,10}$/.test(trimmedSymbol)) {
    throw new ValidationError(
      'Invalid stock symbol format. Use alphanumeric characters (1-10)'
    );
  }

  return trimmedSymbol;
}

/**
 * Validate days parameter
 * @param {number} days - Number of days
 * @throws {ValidationError} If days is invalid
 * @returns {number} Validated days
 */
function validateDays(days) {
  if (days === undefined || days === null) {
    return 30; // Default
  }

  const parsed = parseInt(days, 10);

  if (isNaN(parsed) || parsed < 1 || parsed > 3650) {
    throw new ValidationError('Days must be between 1 and 3650');
  }

  return parsed;
}

/**
 * Validate limit parameter for pagination
 * @param {number} limit - Number of results to return
 * @throws {ValidationError} If limit is invalid
 * @returns {number} Validated limit
 */
function validateLimit(limit) {
  if (limit === undefined || limit === null) {
    return 20; // Default
  }

  const parsed = parseInt(limit, 10);

  if (isNaN(parsed) || parsed < 1 || parsed > 1000) {
    throw new ValidationError('Limit must be between 1 and 1000');
  }

  return parsed;
}

/**
 * Validate debate request
 * @param {object} body - Request body
 * @throws {ValidationError} If request is invalid
 * @returns {object} Validated debate request
 */
function validateDebateRequest(body) {
  if (!body || typeof body !== 'object') {
    throw new ValidationError('Request body is required');
  }

  const { symbol, includeAnalysis } = body;

  if (!symbol) {
    throw new ValidationError('Stock symbol is required');
  }

  validateSymbol(symbol);

  if (
    includeAnalysis &&
    !Array.isArray(includeAnalysis) &&
    includeAnalysis.length > 0
  ) {
    throw new ValidationError('includeAnalysis must be an array');
  }

  const validAnalysisTypes = ['fundamental', 'technical', 'sentiment'];
  if (includeAnalysis) {
    for (const type of includeAnalysis) {
      if (!validAnalysisTypes.includes(type)) {
        throw new ValidationError(
          `Invalid analysis type: ${type}. Must be one of: ${validAnalysisTypes.join(', ')}`
        );
      }
    }
  }

  return {
    symbol: validateSymbol(symbol),
    includeAnalysis: includeAnalysis || validAnalysisTypes,
  };
}

/**
 * Validate email
 * @param {string} email - Email to validate
 * @throws {ValidationError} If email is invalid
 * @returns {string} Validated email
 */
function validateEmail(email) {
  if (!email || !validator.isEmail(email)) {
    throw new ValidationError('Invalid email address');
  }

  return email.toLowerCase();
}

module.exports = {
  validateSymbol,
  validateDays,
  validateLimit,
  validateDebateRequest,
  validateEmail,
};
