/**
 * Input Validation Middleware
 * Validates and sanitizes request data
 */

const logger = require('../utils/logger');

/**
 * Validate stock symbol format
 * Symbols should be 3-5 uppercase letters, optionally followed by .VN
 */
const validateSymbol = (symbol) => {
  if (!symbol || typeof symbol !== 'string') {
    return { valid: false, error: 'Symbol must be a string' };
  }

  const symbolRegex = /^[A-Z]{3,5}(\.VN)?$/;
  if (!symbolRegex.test(symbol.trim().toUpperCase())) {
    return { valid: false, error: 'Invalid symbol format' };
  }

  return { valid: true, symbol: symbol.trim().toUpperCase() };
};

/**
 * Validate limit parameter (pagination)
 */
const validateLimit = (limit) => {
  if (!limit) {
    return { valid: true, limit: 10 };
  }

  const parsed = parseInt(limit, 10);
  if (isNaN(parsed) || parsed < 1 || parsed > 100) {
    return { valid: false, error: 'Limit must be between 1 and 100' };
  }

  return { valid: true, limit: parsed };
};

/**
 * Validate query string parameter
 */
const validateQuery = (query) => {
  if (!query || typeof query !== 'string') {
    return { valid: false, error: 'Query must be a non-empty string' };
  }

  if (query.length < 2 || query.length > 100) {
    return {
      valid: false,
      error: 'Query must be between 2 and 100 characters',
    };
  }

  // Remove potentially dangerous characters
  const sanitized = query.replace(/[<>\"'`]/g, '');
  return { valid: true, query: sanitized };
};

/**
 * Middleware to validate symbol in URL params
 */
const validateSymbolParam = (req, res, next) => {
  const { symbol } = req.params;

  const validation = validateSymbol(symbol);
  if (!validation.valid) {
    logger.warn(`Invalid symbol: ${symbol}`);
    return res.status(400).json({
      success: false,
      error: validation.error,
      code: 'INVALID_SYMBOL',
    });
  }

  req.params.symbol = validation.symbol;
  next();
};

/**
 * Middleware to validate limit query parameter
 */
const validateLimitQuery = (req, res, next) => {
  const { limit } = req.query;

  if (limit) {
    const validation = validateLimit(limit);
    if (!validation.valid) {
      logger.warn(`Invalid limit: ${limit}`);
      return res.status(400).json({
        success: false,
        error: validation.error,
        code: 'INVALID_LIMIT',
      });
    }
    req.query.limit = validation.limit;
  }

  next();
};

/**
 * Middleware to validate query search parameter
 */
const validateQueryParam = (req, res, next) => {
  const { query } = req.query;

  if (query) {
    const validation = validateQuery(query);
    if (!validation.valid) {
      logger.warn(`Invalid query: ${query}`);
      return res.status(400).json({
        success: false,
        error: validation.error,
        code: 'INVALID_QUERY',
      });
    }
    req.query.query = validation.query;
  }

  next();
};

/**
 * Middleware to validate multiple symbols
 */
const validateSymbolsQuery = (req, res, next) => {
  const { symbols } = req.query;

  if (symbols) {
    const symbolList = symbols.split(',').map((s) => s.trim());
    const validations = symbolList.map(validateSymbol);

    const invalid = validations.find((v) => !v.valid);
    if (invalid) {
      logger.warn(`Invalid symbol in list: ${symbols}`);
      return res.status(400).json({
        success: false,
        error: invalid.error,
        code: 'INVALID_SYMBOL',
      });
    }

    req.query.symbols = validations.map((v) => v.symbol);
  }

  next();
};

/**
 * Middleware to log validated request
 */
const logValidation = (req, res, next) => {
  logger.debug(`Validated request: ${req.method} ${req.path}`, {
    params: req.params,
    query: req.query,
  });
  next();
};

module.exports = {
  validateSymbol,
  validateLimit,
  validateQuery,
  validateSymbolParam,
  validateLimitQuery,
  validateQueryParam,
  validateSymbolsQuery,
  logValidation,
};
