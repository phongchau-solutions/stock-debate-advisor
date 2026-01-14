/**
 * JWT Authentication Middleware
 * Validates JWT tokens from frontend requests
 */

const jwt = require('jsonwebtoken');
const config = require('../config');
const logger = require('../utils/logger');

/**
 * Verify JWT token middleware
 */
const authenticateToken = (req, res, next) => {
  try {
    // Get token from Authorization header
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      logger.warn('Missing authentication token');
      return res.status(401).json({
        success: false,
        error: 'Access token required',
        code: 'MISSING_TOKEN',
      });
    }

    // Verify token
    jwt.verify(token, config.auth.jwtSecret, (err, user) => {
      if (err) {
        logger.warn(`Token verification failed: ${err.message}`);
        if (err.name === 'TokenExpiredError') {
          return res.status(401).json({
            success: false,
            error: 'Token expired',
            code: 'TOKEN_EXPIRED',
          });
        }
        return res.status(403).json({
          success: false,
          error: 'Invalid token',
          code: 'INVALID_TOKEN',
        });
      }

      // Attach user info to request
      req.user = user;
      logger.debug(`Authenticated user: ${user.id}`);
      next();
    });
  } catch (error) {
    logger.error(`Authentication error: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: 'Authentication error',
    });
  }
};

/**
 * Generate JWT token (for login endpoints)
 * @param {object} user - User object {id, email, role, ...}
 * @param {string} expiresIn - Token expiry (default: '24h')
 * @returns {string} JWT token
 */
const generateToken = (user, expiresIn = config.auth.jwtExpiry) => {
  return jwt.sign(
    {
      id: user.id,
      email: user.email,
      role: user.role || 'user',
    },
    config.auth.jwtSecret,
    { expiresIn }
  );
};

/**
 * Optional authentication - doesn't fail if token is missing
 */
const authenticateTokenOptional = (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token) {
      jwt.verify(token, config.auth.jwtSecret, (err, user) => {
        if (!err) {
          req.user = user;
          logger.debug(`Optional auth: User ${user.id} authenticated`);
        } else {
          logger.debug(
            `Optional auth: Invalid token, continuing as unauthenticated`
          );
        }
      });
    }

    next();
  } catch (error) {
    logger.error(`Optional auth error: ${error.message}`);
    next(); // Continue even if error
  }
};

/**
 * Check if user has required role
 * @param {string|string[]} requiredRoles - Required role(s)
 * @returns {function} Middleware function
 */
const requireRole = (requiredRoles) => {
  const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles];

  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        error: 'Authentication required',
      });
    }

    if (!roles.includes(req.user.role)) {
      logger.warn(
        `User ${req.user.id} lacks required role. Required: ${roles}, Has: ${req.user.role}`
      );
      return res.status(403).json({
        success: false,
        error: 'Insufficient permissions',
        code: 'INSUFFICIENT_PERMISSIONS',
      });
    }

    next();
  };
};

module.exports = {
  authenticateToken,
  authenticateTokenOptional,
  generateToken,
  requireRole,
};
