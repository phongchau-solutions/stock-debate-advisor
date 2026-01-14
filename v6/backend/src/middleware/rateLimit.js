/**
 * Rate Limiting Middleware
 * Implements per-user and per-IP rate limiting
 */

const logger = require('../utils/logger');

/**
 * In-memory rate limit store
 * In production, use Redis for distributed rate limiting
 */
class RateLimitStore {
  constructor() {
    this.limits = new Map();
    // Clean up expired entries every minute
    setInterval(() => this.cleanup(), 60000);
  }

  /**
   * Get current count for a key
   */
  getCount(key) {
    const entry = this.limits.get(key);
    if (!entry) return 0;
    if (Date.now() > entry.resetTime) {
      this.limits.delete(key);
      return 0;
    }
    return entry.count;
  }

  /**
   * Increment count and check if limit exceeded
   */
  checkLimit(key, maxRequests, windowMs) {
    let entry = this.limits.get(key);

    if (!entry || Date.now() > entry.resetTime) {
      entry = {
        count: 1,
        resetTime: Date.now() + windowMs,
      };
      this.limits.set(key, entry);
      return { exceeded: false, count: 1 };
    }

    entry.count += 1;
    const exceeded = entry.count > maxRequests;

    return {
      exceeded,
      count: entry.count,
      resetTime: entry.resetTime,
    };
  }

  /**
   * Get time until reset
   */
  getResetTime(key) {
    const entry = this.limits.get(key);
    if (!entry) return null;
    return Math.ceil((entry.resetTime - Date.now()) / 1000);
  }

  /**
   * Clean up expired entries
   */
  cleanup() {
    const now = Date.now();
    for (const [key, entry] of this.limits.entries()) {
      if (now > entry.resetTime) {
        this.limits.delete(key);
      }
    }
  }
}

const store = new RateLimitStore();

/**
 * Rate limiting middleware - per user (requires authentication)
 */
const rateLimitPerUser = (options = {}) => {
  const maxRequests = options.maxRequests || 100;
  const windowMs = options.windowMs || 900000; // 15 minutes

  return (req, res, next) => {
    // Only rate limit authenticated users
    if (!req.user) {
      return next();
    }

    const key = `user:${req.user.id}`;
    const result = store.checkLimit(key, maxRequests, windowMs);

    // Set rate limit headers
    res.set('X-RateLimit-Limit', maxRequests);
    res.set('X-RateLimit-Remaining', Math.max(0, maxRequests - result.count));
    res.set('X-RateLimit-Reset', new Date(result.resetTime).toISOString());

    if (result.exceeded) {
      logger.warn(`Rate limit exceeded for user ${req.user.id}`);
      return res.status(429).json({
        success: false,
        error: 'Too many requests',
        code: 'RATE_LIMIT_EXCEEDED',
        retryAfter: store.getResetTime(key),
      });
    }

    logger.debug(
      `Rate limit: user ${req.user.id} - ${result.count}/${maxRequests}`
    );
    next();
  };
};

/**
 * Rate limiting middleware - per IP (for unauthenticated requests)
 */
const rateLimitPerIP = (options = {}) => {
  const maxRequests = options.maxRequests || 50;
  const windowMs = options.windowMs || 900000; // 15 minutes

  return (req, res, next) => {
    const ip = req.ip || req.connection.remoteAddress;
    const key = `ip:${ip}`;
    const result = store.checkLimit(key, maxRequests, windowMs);

    // Set rate limit headers
    res.set('X-RateLimit-Limit', maxRequests);
    res.set('X-RateLimit-Remaining', Math.max(0, maxRequests - result.count));
    res.set('X-RateLimit-Reset', new Date(result.resetTime).toISOString());

    if (result.exceeded) {
      logger.warn(`Rate limit exceeded for IP ${ip}`);
      return res.status(429).json({
        success: false,
        error: 'Too many requests',
        code: 'RATE_LIMIT_EXCEEDED',
        retryAfter: store.getResetTime(key),
      });
    }

    logger.debug(`Rate limit: IP ${ip} - ${result.count}/${maxRequests}`);
    next();
  };
};

/**
 * Combined rate limiting (per user if authenticated, per IP otherwise)
 */
const rateLimitCombined = (options = {}) => {
  const userMaxRequests = options.userMaxRequests || 100;
  const userWindowMs = options.userWindowMs || 900000;
  const ipMaxRequests = options.ipMaxRequests || 50;
  const ipWindowMs = options.ipWindowMs || 900000;

  return (req, res, next) => {
    let key, maxRequests, windowMs;

    if (req.user) {
      key = `user:${req.user.id}`;
      maxRequests = userMaxRequests;
      windowMs = userWindowMs;
    } else {
      key = `ip:${req.ip || req.connection.remoteAddress}`;
      maxRequests = ipMaxRequests;
      windowMs = ipWindowMs;
    }

    const result = store.checkLimit(key, maxRequests, windowMs);

    // Set rate limit headers
    res.set('X-RateLimit-Limit', maxRequests);
    res.set('X-RateLimit-Remaining', Math.max(0, maxRequests - result.count));
    res.set('X-RateLimit-Reset', new Date(result.resetTime).toISOString());

    if (result.exceeded) {
      const identifier = req.user ? `user ${req.user.id}` : `IP ${key}`;
      logger.warn(`Rate limit exceeded for ${identifier}`);
      return res.status(429).json({
        success: false,
        error: 'Too many requests',
        code: 'RATE_LIMIT_EXCEEDED',
        retryAfter: store.getResetTime(key),
      });
    }

    next();
  };
};

module.exports = {
  rateLimitPerUser,
  rateLimitPerIP,
  rateLimitCombined,
  store,
};
