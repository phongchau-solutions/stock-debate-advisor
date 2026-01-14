/**
 * Financial data routes
 * Secured routes with authentication, validation, and rate limiting
 */

const express = require('express');
const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/errorHandler');
const { authenticateTokenOptional } = require('../middleware/auth');
const {
  validateSymbolParam,
  validateLimitQuery,
} = require('../middleware/validation');
const { rateLimitCombined } = require('../middleware/rateLimit');
const dataServiceClient = require('../services/dataServiceClient');

const router = express.Router();

// Apply middleware to all routes
router.use(authenticateTokenOptional);
router.use(rateLimitCombined());
router.use((req, res, next) => {
  logger.debug(`Financials route: ${req.method} ${req.path}`, {
    user: req.user?.id || 'anonymous',
  });
  next();
});

/**
 * Get all financial data
 * @route GET /api/v1/financials/:symbol
 */
router.get(
  '/:symbol',
  validateSymbolParam,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;

    logger.info(`Fetching all financial data for ${symbol}`, {
      user: req.user?.id || 'anonymous',
    });

    try {
      const data = await dataServiceClient.getFinancials(symbol);

      if (!data) {
        return res.status(404).json({
          success: false,
          error: `Financial data not found for ${symbol}`,
          code: 'NOT_FOUND',
        });
      }

      res.json({
        success: true,
        data,
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
 * Get quarterly financial reports
 * @route GET /api/v1/financials/:symbol/quarterly?limit=8
 */
router.get(
  '/:symbol/quarterly',
  validateSymbolParam,
  validateLimitQuery,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;
    const { limit = 8 } = req.query;

    logger.info(`Fetching quarterly reports for ${symbol} (limit: ${limit})`, {
      user: req.user?.id || 'anonymous',
    });

    try {
      const reports = await dataServiceClient.getQuarterlyReports(
        symbol,
        limit
      );

      if (!reports) {
        return res.status(404).json({
          success: false,
          error: `Quarterly reports not found for ${symbol}`,
          code: 'NOT_FOUND',
        });
      }

      res.json({
        success: true,
        data: reports,
      });
    } catch (error) {
      logger.error(
        `Error fetching quarterly reports for ${symbol}: ${error.message}`
      );
      res.status(500).json({
        success: false,
        error: 'Failed to fetch quarterly reports',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

/**
 * Get annual financial reports
 * @route GET /api/v1/financials/:symbol/annual?limit=5
 */
router.get(
  '/:symbol/annual',
  validateSymbolParam,
  validateLimitQuery,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;
    const { limit = 5 } = req.query;

    logger.info(`Fetching annual reports for ${symbol} (limit: ${limit})`, {
      user: req.user?.id || 'anonymous',
    });

    try {
      const reports = await dataServiceClient.getAnnualReports(symbol, limit);

      if (!reports) {
        return res.status(404).json({
          success: false,
          error: `Annual reports not found for ${symbol}`,
          code: 'NOT_FOUND',
        });
      }

      res.json({
        success: true,
        data: reports,
      });
    } catch (error) {
      logger.error(
        `Error fetching annual reports for ${symbol}: ${error.message}`
      );
      res.status(500).json({
        success: false,
        error: 'Failed to fetch annual reports',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

/**
 * Get financial metrics
 * @route GET /api/v1/financials/:symbol/metrics
 */
router.get(
  '/:symbol/metrics',
  validateSymbolParam,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;

    logger.info(`Fetching financial metrics for ${symbol}`, {
      user: req.user?.id || 'anonymous',
    });

    try {
      const metrics = await dataServiceClient.getFinancialMetrics(symbol);

      if (!metrics) {
        return res.status(404).json({
          success: false,
          error: `Financial metrics not found for ${symbol}`,
          code: 'NOT_FOUND',
        });
      }

      res.json({
        success: true,
        data: metrics,
      });
    } catch (error) {
      logger.error(
        `Error fetching financial metrics for ${symbol}: ${error.message}`
      );
      res.status(500).json({
        success: false,
        error: 'Failed to fetch financial metrics',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

/**
 * Get dividends
 * @route GET /api/v1/financials/:symbol/dividends
 */
router.get(
  '/:symbol/dividends',
  validateSymbolParam,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;

    logger.info(`Fetching dividends for ${symbol}`, {
      user: req.user?.id || 'anonymous',
    });

    try {
      const dividends = await dataServiceClient.getDividends(symbol);

      res.json({
        success: true,
        data: dividends || [],
      });
    } catch (error) {
      logger.error(`Error fetching dividends for ${symbol}: ${error.message}`);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch dividend data',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

/**
 * Get stock splits
 * @route GET /api/v1/financials/:symbol/splits
 */
router.get(
  '/:symbol/splits',
  validateSymbolParam,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;

    logger.info(`Fetching stock splits for ${symbol}`, {
      user: req.user?.id || 'anonymous',
    });

    try {
      const splits = await dataServiceClient.getStockSplits(symbol);

      res.json({
        success: true,
        data: splits || [],
      });
    } catch (error) {
      logger.error(
        `Error fetching stock splits for ${symbol}: ${error.message}`
      );
      res.status(500).json({
        success: false,
        error: 'Failed to fetch stock split data',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

/**
 * Get price data
 * @route GET /api/v1/financials/:symbol/prices?limit=30
 */
router.get(
  '/:symbol/prices',
  validateSymbolParam,
  validateLimitQuery,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;
    const { limit = 30 } = req.query;

    logger.info(`Fetching price data for ${symbol} (${limit} records)`, {
      user: req.user?.id || 'anonymous',
    });

    try {
      const prices = await dataServiceClient.getPriceData(symbol, limit);

      if (!prices) {
        return res.status(404).json({
          success: false,
          error: `Price data not found for ${symbol}`,
          code: 'NOT_FOUND',
        });
      }

      res.json({
        success: true,
        data: prices,
      });
    } catch (error) {
      logger.error(`Error fetching price data for ${symbol}: ${error.message}`);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch price data',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

/**
 * Get news
 * @route GET /api/v1/financials/:symbol/news
 */
router.get(
  '/:symbol/news',
  validateSymbolParam,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;

    logger.info(`Fetching news for ${symbol}`, {
      user: req.user?.id || 'anonymous',
    });

    try {
      const news = await dataServiceClient.getNews(symbol);

      res.json({
        success: true,
        data: news || [],
      });
    } catch (error) {
      logger.error(`Error fetching news for ${symbol}: ${error.message}`);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch news data',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

/**
 * Get complete stock data
 * @route GET /api/v1/financials/:symbol/full
 */
router.get(
  '/:symbol/full',
  validateSymbolParam,
  asyncHandler(async (req, res) => {
    const { symbol } = req.params;

    logger.info(`Fetching complete data for ${symbol}`, {
      user: req.user?.id || 'anonymous',
    });

    try {
      const data = await dataServiceClient.getFullStockData(symbol);

      if (!data) {
        return res.status(404).json({
          success: false,
          error: `Data not found for ${symbol}`,
          code: 'NOT_FOUND',
        });
      }

      res.json({
        success: true,
        data,
      });
    } catch (error) {
      logger.error(
        `Error fetching complete data for ${symbol}: ${error.message}`
      );
      res.status(500).json({
        success: false,
        error: 'Failed to fetch complete data',
        code: 'SERVICE_ERROR',
      });
    }
  })
);

module.exports = router;
