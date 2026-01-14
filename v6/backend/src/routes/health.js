/**
 * Health check routes
 */

const express = require('express');
const logger = require('../utils/logger');
const dataServiceClient = require('../services/dataServiceClient');
const aiServiceClient = require('../services/aiServiceClient');

const router = express.Router();

/**
 * Health check endpoint
 * @route GET /health
 */
router.get('/', async (req, res) => {
  try {
    // Check data service health
    let dataServiceStatus = 'unknown';
    try {
      await dataServiceClient.client.get('/');
      dataServiceStatus = 'up';
    } catch (error) {
      dataServiceStatus = 'down';
      logger.warn(`Data Service health check failed: ${error.message}`);
    }

    // Check AI service health
    let aiServiceStatus = 'unknown';
    try {
      await aiServiceClient.client.get('/');
      aiServiceStatus = 'up';
    } catch (error) {
      aiServiceStatus = 'down';
      logger.warn(`AI Service health check failed: ${error.message}`);
    }

    const status = {
      status:
        dataServiceStatus === 'up' && aiServiceStatus === 'up'
          ? 'ok'
          : 'partial',
      timestamp: new Date().toISOString(),
      services: {
        'data-service': dataServiceStatus,
        'ai-service': aiServiceStatus,
      },
    };

    const httpStatus =
      dataServiceStatus === 'up' && aiServiceStatus === 'up' ? 200 : 503;
    res.status(httpStatus).json(status);
  } catch (error) {
    logger.error(`Health check error: ${error.message}`);
    res.status(500).json({
      status: 'error',
      timestamp: new Date().toISOString(),
      message: error.message,
    });
  }
});

/**
 * Version endpoint
 * @route GET /version
 */
router.get('/version', (req, res) => {
  res.json({
    service: 'Stock Debate Advisor Backend',
    version: '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString(),
  });
});

/**
 * Status endpoint
 * @route GET /status
 */
router.get('/status', (req, res) => {
  res.json({
    status: 'running',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    timestamp: new Date().toISOString(),
  });
});

module.exports = router;
