/**
 * Analysis/Debate routes
 */

const express = require('express');
const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/errorHandler');
const { validateDebateRequest } = require('../utils/validators');
const dataServiceClient = require('../services/dataServiceClient');
const aiServiceClient = require('../services/aiServiceClient');

const router = express.Router();

/**
 * Start a debate session
 * @route POST /api/v1/debate/start
 */
router.post(
  '/start',
  asyncHandler(async (req, res) => {
    const { symbol, includeAnalysis } = validateDebateRequest(req.body);

    logger.info(`Starting debate for ${symbol}`);

    // Fetch company data to include in request
    let companyData = {};
    try {
      companyData = await dataServiceClient.getCompany(symbol);
    } catch (error) {
      logger.warn(
        `Could not fetch company data for ${symbol}: ${error.message}`
      );
    }

    // Start debate in AI service
    const debateSession = await aiServiceClient.startDebate(
      symbol,
      includeAnalysis
    );

    res.status(201).json({
      success: true,
      data: {
        sessionId: debateSession.sessionId,
        symbol,
        company: companyData,
        analysisTypes: includeAnalysis,
        status: 'started',
        createdAt: new Date().toISOString(),
      },
    });
  })
);

/**
 * Get debate session details
 * @route GET /api/v1/debate/:sessionId
 */
router.get(
  '/:sessionId',
  asyncHandler(async (req, res) => {
    const { sessionId } = req.params;

    logger.debug(`Fetching debate session: ${sessionId}`);

    const session = await aiServiceClient.getDebateSession(sessionId);

    res.json({
      success: true,
      data: session,
    });
  })
);

/**
 * Get debate session status
 * @route GET /api/v1/debate/:sessionId/status
 */
router.get(
  '/:sessionId/status',
  asyncHandler(async (req, res) => {
    const { sessionId } = req.params;

    logger.debug(`Fetching debate status: ${sessionId}`);

    const status = await aiServiceClient.getDebateStatus(sessionId);

    res.json({
      success: true,
      data: status,
    });
  })
);

/**
 * Get fundamental analysis
 * @route GET /api/v1/debate/:sessionId/fundamental
 */
router.get(
  '/:sessionId/fundamental',
  asyncHandler(async (req, res) => {
    const { sessionId } = req.params;

    logger.debug(`Fetching fundamental analysis for session: ${sessionId}`);

    const knowledge = await aiServiceClient.getFundamentalKnowledge(sessionId);

    res.json({
      success: true,
      data: knowledge,
    });
  })
);

/**
 * Get technical analysis
 * @route GET /api/v1/debate/:sessionId/technical
 */
router.get(
  '/:sessionId/technical',
  asyncHandler(async (req, res) => {
    const { sessionId } = req.params;

    logger.debug(`Fetching technical analysis for session: ${sessionId}`);

    const knowledge = await aiServiceClient.getTechnicalKnowledge(sessionId);

    res.json({
      success: true,
      data: knowledge,
    });
  })
);

/**
 * Get sentiment analysis
 * @route GET /api/v1/debate/:sessionId/sentiment
 */
router.get(
  '/:sessionId/sentiment',
  asyncHandler(async (req, res) => {
    const { sessionId } = req.params;

    logger.debug(`Fetching sentiment analysis for session: ${sessionId}`);

    const knowledge = await aiServiceClient.getSentimentKnowledge(sessionId);

    res.json({
      success: true,
      data: knowledge,
    });
  })
);

module.exports = router;
