/**
 * Session management routes
 */

const express = require('express');
const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/errorHandler');

const router = express.Router();

// In-memory session store (replace with database in production)
const sessions = new Map();

/**
 * Get all sessions
 * @route GET /api/v1/sessions
 */
router.get(
  '/',
  asyncHandler(async (req, res) => {
    logger.debug('Fetching all sessions');

    const sessionList = Array.from(sessions.values()).map((session) => ({
      id: session.id,
      symbol: session.symbol,
      status: session.status,
      createdAt: session.createdAt,
      updatedAt: session.updatedAt,
    }));

    res.json({
      success: true,
      data: sessionList,
      total: sessionList.length,
    });
  })
);

/**
 * Get session details
 * @route GET /api/v1/sessions/:sessionId
 */
router.get(
  '/:sessionId',
  asyncHandler(async (req, res) => {
    const { sessionId } = req.params;

    logger.debug(`Fetching session: ${sessionId}`);

    const session = sessions.get(sessionId);

    if (!session) {
      return res.status(404).json({
        success: false,
        error: {
          status: 404,
          message: 'Session not found',
        },
      });
    }

    res.json({
      success: true,
      data: session,
    });
  })
);

/**
 * Create a new session
 * @route POST /api/v1/sessions
 */
router.post(
  '/',
  asyncHandler(async (req, res) => {
    const { symbol, debateSessionId } = req.body;

    if (!symbol || !debateSessionId) {
      return res.status(400).json({
        success: false,
        error: {
          status: 400,
          message: 'symbol and debateSessionId are required',
        },
      });
    }

    const sessionId = uuidv4();
    const session = {
      id: sessionId,
      symbol,
      debateSessionId,
      status: 'active',
      rating: null,
      feedback: null,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    sessions.set(sessionId, session);
    logger.info(`Session created: ${sessionId} for ${symbol}`);

    res.status(201).json({
      success: true,
      data: session,
    });
  })
);

/**
 * Rate a session
 * @route POST /api/v1/sessions/:sessionId/rate
 */
router.post(
  '/:sessionId/rate',
  asyncHandler(async (req, res) => {
    const { sessionId } = req.params;
    const { rating, feedback } = req.body;

    if (!rating || rating < 1 || rating > 5) {
      return res.status(400).json({
        success: false,
        error: {
          status: 400,
          message: 'rating must be between 1 and 5',
        },
      });
    }

    const session = sessions.get(sessionId);

    if (!session) {
      return res.status(404).json({
        success: false,
        error: {
          status: 404,
          message: 'Session not found',
        },
      });
    }

    session.rating = rating;
    session.feedback = feedback || null;
    session.updatedAt = new Date().toISOString();
    session.status = 'closed';

    sessions.set(sessionId, session);
    logger.info(`Session rated: ${sessionId} with rating: ${rating}`);

    res.json({
      success: true,
      data: session,
    });
  })
);

/**
 * Export session data
 * @route GET /api/v1/sessions/:sessionId/export
 */
router.get(
  '/:sessionId/export',
  asyncHandler(async (req, res) => {
    const { sessionId } = req.params;
    const { format = 'json' } = req.query;

    const session = sessions.get(sessionId);

    if (!session) {
      return res.status(404).json({
        success: false,
        error: {
          status: 404,
          message: 'Session not found',
        },
      });
    }

    logger.info(`Exporting session: ${sessionId} as ${format}`);

    if (format === 'csv') {
      const csv = `Session ID,Symbol,Status,Rating,Created At,Updated At\n${session.id},${session.symbol},${session.status},${session.rating || 'N/A'},${session.createdAt},${session.updatedAt}`;

      res.setHeader('Content-Type', 'text/csv');
      res.setHeader(
        'Content-Disposition',
        `attachment; filename="session-${sessionId}.csv"`
      );
      res.send(csv);
    } else {
      res.json({
        success: true,
        data: session,
      });
    }
  })
);

module.exports = router;
