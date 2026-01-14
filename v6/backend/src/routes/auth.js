/**
 * Authentication routes
 * Provides JWT token generation and user authentication
 */

const express = require('express');
const logger = require('../utils/logger');
const { generateToken, authenticateToken } = require('../middleware/auth');
const { asyncHandler } = require('../middleware/errorHandler');

const router = express.Router();

/**
 * Login endpoint - returns JWT token
 * @route POST /api/v1/auth/login
 * @body {string} email - User email
 * @body {string} password - User password
 * @returns {object} JWT token
 */
router.post(
  '/login',
  asyncHandler(async (req, res) => {
    const { email, password } = req.body;

    // Basic validation
    if (!email || !password) {
      logger.warn('Login attempt with missing credentials');
      return res.status(400).json({
        success: false,
        error: 'Email and password required',
        code: 'MISSING_CREDENTIALS',
      });
    }

    // In production, validate against database
    // For demo purposes, accept any email/password
    if (password.length < 6) {
      return res.status(400).json({
        success: false,
        error: 'Password must be at least 6 characters',
        code: 'INVALID_PASSWORD',
      });
    }

    try {
      // Create mock user object
      // In production, fetch from database
      const user = {
        id: email.split('@')[0],
        email,
        role: 'user',
      };

      const token = generateToken(user);

      logger.info(`User logged in: ${email}`);

      res.json({
        success: true,
        data: {
          token,
          user: {
            id: user.id,
            email: user.email,
            role: user.role,
          },
        },
      });
    } catch (error) {
      logger.error(`Login error: ${error.message}`);
      res.status(500).json({
        success: false,
        error: 'Authentication failed',
      });
    }
  })
);

/**
 * Verify token endpoint
 * @route GET /api/v1/auth/verify
 * @header {string} Authorization - Bearer token
 * @returns {object} Token validity and user info
 */
router.get(
  '/verify',
  authenticateToken,
  asyncHandler(async (req, res) => {
    res.json({
      success: true,
      data: {
        valid: true,
        user: req.user,
      },
    });
  })
);

/**
 * Refresh token endpoint
 * @route POST /api/v1/auth/refresh
 * @header {string} Authorization - Bearer token
 * @returns {object} New JWT token
 */
router.post(
  '/refresh',
  authenticateToken,
  asyncHandler(async (req, res) => {
    try {
      const newToken = generateToken(req.user);

      logger.info(`Token refreshed for user: ${req.user.id}`);

      res.json({
        success: true,
        data: {
          token: newToken,
        },
      });
    } catch (error) {
      logger.error(`Token refresh error: ${error.message}`);
      res.status(500).json({
        success: false,
        error: 'Token refresh failed',
      });
    }
  })
);

/**
 * Register endpoint
 * @route POST /api/v1/auth/register
 * @body {string} email - User email
 * @body {string} password - User password
 * @body {string} name - User name (optional)
 * @returns {object} JWT token
 */
router.post(
  '/register',
  asyncHandler(async (req, res) => {
    const { email, password, name } = req.body;

    // Validation
    if (!email || !password) {
      return res.status(400).json({
        success: false,
        error: 'Email and password required',
        code: 'MISSING_CREDENTIALS',
      });
    }

    if (password.length < 6) {
      return res.status(400).json({
        success: false,
        error: 'Password must be at least 6 characters',
        code: 'INVALID_PASSWORD',
      });
    }

    if (!email.includes('@')) {
      return res.status(400).json({
        success: false,
        error: 'Invalid email format',
        code: 'INVALID_EMAIL',
      });
    }

    try {
      // In production, save user to database and check for duplicates
      const user = {
        id: email.split('@')[0],
        email,
        name: name || email.split('@')[0],
        role: 'user',
      };

      const token = generateToken(user);

      logger.info(`User registered: ${email}`);

      res.status(201).json({
        success: true,
        data: {
          token,
          user: {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
          },
        },
      });
    } catch (error) {
      logger.error(`Registration error: ${error.message}`);
      res.status(500).json({
        success: false,
        error: 'Registration failed',
      });
    }
  })
);

module.exports = router;
