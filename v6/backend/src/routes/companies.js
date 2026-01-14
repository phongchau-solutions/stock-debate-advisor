/**
 * Company info routes
 * Secured routes with authentication, validation, and rate limiting
 */

const express = require('express');
const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/errorHandler');
const { authenticateTokenOptional } = require('../middleware/auth');
const {
  validateSymbolParam,
  validateSymbolsQuery,
} = require('../middleware/validation');
const { rateLimitCombined } = require('../middleware/rateLimit');
const dataServiceClient = require('../services/dataServiceClient');

const router = express.Router();

// Apply middleware to all routes in this router
router.use(authenticateTokenOptional); // Optional auth - allows both authenticated and unauthenticated users
router.use(rateLimitCombined()); // Rate limiting per user or IP
router.use((req, res, next) => {
  // Log incoming requests
  logger.debug(`Companies route: ${req.method} ${req.path}`, {
    user: req.user?.id || 'anonymous',
    ip: req.ip,
  });
  next();
});

/**
 * Get company information
 * @route GET /api/v1/companies/:symbol
 * @param {string} symbol - Stock symbol (e.g., ACB, MBB.VN)
 * @returns {object} Company information
 */
router.get(
  '/:symbol',
  validateSymbolParam,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;

    logger.info(`Fetching company info for ${symbol}`, {
      user: req.user?.id || 'anonymous',
    });

    try {
      const company = await dataServiceClient.getCompany(symbol);

      if (!company) {
        return res.status(404).json({
          success: false,
          error: `Company not found: ${symbol}`,
          code: 'NOT_FOUND',
        });
      }

      logger.debug(`Company info retrieved for ${symbol}`);
      res.json({
        success: true,
        data: company,
      });
    } catch (error) {
      logger.error(`Error fetching company ${symbol}: ${error.message}`);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch company information',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

/**
 * Get company financials
 * @route GET /api/v1/companies/:symbol/financials
 * @param {string} symbol - Stock symbol
 * @returns {object} Financial data
 */
router.get(
  '/:symbol/financials',
  validateSymbolParam,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;

    logger.info(`Fetching financials for ${symbol}`, {
      user: req.user?.id || 'anonymous',
    });

    try {
      const financials = await dataServiceClient.getFinancials(symbol);

      if (!financials) {
        return res.status(404).json({
          success: false,
          error: `Financials not found: ${symbol}`,
          code: 'NOT_FOUND',
        });
      }

      res.json({
        success: true,
        data: financials,
      });
    } catch (error) {
      logger.error(`Error fetching financials for ${symbol}: ${error.message}`);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch financial data',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

/**
 * Get multiple companies
 * @route GET /api/v1/companies?symbols=MBB,VCB,FPT
 * @param {string} symbols - Comma-separated stock symbols
 * @returns {object[]} Array of company information
 */
router.get(
  '/',
  validateSymbolsQuery,
  asyncHandler(async (req, res) => {
    const { symbols } = req.query;

    if (!symbols || symbols.length === 0) {
      logger.debug('No symbols provided');
      return res.json({
        success: true,
        data: [],
      });
    }

    logger.info(`Fetching company info for: ${symbols.join(', ')}`, {
      user: req.user?.id || 'anonymous',
      count: symbols.length,
    });

    try {
      const companies = await Promise.all(
        symbols.map((symbol) =>
          dataServiceClient.getCompany(symbol).catch((error) => ({
            symbol,
            error: error.message,
            success: false,
          }))
        )
      );

      // Separate successful and failed responses
      const successful = companies.filter((c) => c && !c.error);
      const failed = companies.filter((c) => c && c.error);

      if (failed.length > 0) {
        logger.warn(`Failed to fetch ${failed.length} companies`, {
          failed: failed.map((c) => c.symbol),
        });
      }

      res.json({
        success: true,
        data: successful,
        errors: failed.length > 0 ? failed : undefined,
      });
    } catch (error) {
      logger.error(`Error fetching multiple companies: ${error.message}`);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch company information',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

/**
 * Search companies
 * @route GET /api/v1/companies/search?query=MBB
 * @param {string} query - Search query
 * @param {number} limit - Results limit (default: 10, max: 50)
 * @returns {object[]} Search results
 */
router.get(
  '/search/query',
  asyncHandler(async (req, res) => {
    const { query, limit = 10 } = req.query;

    if (!query || query.length < 2) {
      return res.status(400).json({
        success: false,
        error: 'Query must be at least 2 characters',
        code: 'INVALID_QUERY',
      });
    }

    const parsedLimit = Math.min(parseInt(limit, 10) || 10, 50);

    logger.info(`Searching companies with query: ${query}`, {
      user: req.user?.id || 'anonymous',
      limit: parsedLimit,
    });

    try {
      const results = await dataServiceClient.searchCompanies(
        query,
        parsedLimit
      );

      res.json({
        success: true,
        data: results,
        query,
      });
    } catch (error) {
      logger.error(`Error searching companies: ${error.message}`);
      res.status(500).json({
        success: false,
        error: 'Failed to search companies',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

/**
 * List all stocks
 * @route GET /api/v1/companies/list/all
 * @returns {object[]} List of all stocks
 */
router.get(
  '/list/all',
  asyncHandler(async (req, res) => {
    logger.info('Fetching all stocks list', {
      user: req.user?.id || 'anonymous',
    });

    try {
      const stocks = await dataServiceClient.getStocks();

      res.json({
        success: true,
        data: stocks,
      });
    } catch (error) {
      logger.error(`Error fetching stocks list: ${error.message}`);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch stocks list',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

module.exports = router;
