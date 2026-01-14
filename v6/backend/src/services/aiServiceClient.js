/**
 * Service client for AI Service communication
 */

const axios = require('axios');
const config = require('../config');
const logger = require('../utils/logger');
const {
  ServiceError,
  TimeoutError,
  NotFoundError,
} = require('../utils/errors');

class AiServiceClient {
  constructor() {
    this.baseURL = config.services.aiService.url;
    this.timeout = config.services.aiService.timeout;
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: this.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Start a debate session
   * @param {string} symbol - Stock symbol
   * @param {string[]} analysisTypes - Types of analysis to include (deprecated, for compatibility)
   * @returns {Promise<object>} Session information
   */
  async startDebate(
    symbol,
    analysisTypes = ['fundamental', 'technical', 'sentiment']
  ) {
    try {
      logger.debug(`Starting debate for ${symbol}`);
      const response = await this.client.post('/api/debate/start', {
        symbol,
        rounds: 2, // Default to 2 rounds for debate
      });
      logger.debug(`Debate started for ${symbol}: ${response.data.session_id}`);
      return {
        sessionId: response.data.session_id,
        ...response.data,
      };
    } catch (error) {
      this.handleError(error, 'startDebate');
    }
  }

  /**
   * Get debate session information
   * @param {string} sessionId - Session ID
   * @returns {Promise<object>} Session information
   */
  async getDebateSession(sessionId) {
    try {
      logger.debug(`Fetching debate session: ${sessionId}`);
      const response = await this.client.get(`/api/v1/debate/${sessionId}`);
      logger.debug(`Debate session fetched: ${sessionId}`);
      return response.data;
    } catch (error) {
      this.handleError(error, 'getDebateSession');
    }
  }

  /**
   * Get debate session status
   * @param {string} sessionId - Session ID
   * @returns {Promise<object>} Session status
   */
  async getDebateStatus(sessionId) {
    try {
      logger.debug(`Fetching debate status: ${sessionId}`);
      const response = await this.client.get(
        `/api/v1/debate/${sessionId}/status`
      );
      logger.debug(`Debate status fetched: ${sessionId}`);
      return response.data;
    } catch (error) {
      this.handleError(error, 'getDebateStatus');
    }
  }

  /**
   * Get session info
   * @param {string} sessionId - Session ID
   * @returns {Promise<object>} Session info
   */
  async getSessionInfo(sessionId) {
    try {
      logger.debug(`Fetching session info: ${sessionId}`);
      const response = await this.client.get(`/api/session/${sessionId}`);
      logger.debug(`Session info fetched: ${sessionId}`);
      return response.data;
    } catch (error) {
      this.handleError(error, 'getSessionInfo');
    }
  }

  /**
   * Get fundamental analysis knowledge
   * @param {string} sessionId - Session ID
   * @returns {Promise<object>} Knowledge data
   */
  async getFundamentalKnowledge(sessionId) {
    try {
      logger.debug(`Fetching fundamental knowledge for session: ${sessionId}`);
      const response = await this.client.get(
        `/api/session/${sessionId}/knowledge/fundamental`
      );
      logger.debug(`Fundamental knowledge fetched for session: ${sessionId}`);
      return response.data;
    } catch (error) {
      this.handleError(error, 'getFundamentalKnowledge');
    }
  }

  /**
   * Get technical analysis knowledge
   * @param {string} sessionId - Session ID
   * @returns {Promise<object>} Knowledge data
   */
  async getTechnicalKnowledge(sessionId) {
    try {
      logger.debug(`Fetching technical knowledge for session: ${sessionId}`);
      const response = await this.client.get(
        `/api/session/${sessionId}/knowledge/technical`
      );
      logger.debug(`Technical knowledge fetched for session: ${sessionId}`);
      return response.data;
    } catch (error) {
      this.handleError(error, 'getTechnicalKnowledge');
    }
  }

  /**
   * Get sentiment analysis knowledge
   * @param {string} sessionId - Session ID
   * @returns {Promise<object>} Knowledge data
   */
  async getSentimentKnowledge(sessionId) {
    try {
      logger.debug(`Fetching sentiment knowledge for session: ${sessionId}`);
      const response = await this.client.get(
        `/api/session/${sessionId}/knowledge/sentiment`
      );
      logger.debug(`Sentiment knowledge fetched for session: ${sessionId}`);
      return response.data;
    } catch (error) {
      this.handleError(error, 'getSentimentKnowledge');
    }
  }

  /**
   * Handle errors from AI service
   * @private
   */
  handleError(error, operation) {
    logger.error(`AI Service error in ${operation}: ${error.message}`);

    if (error.code === 'ECONNABORTED') {
      throw new TimeoutError('AI Service');
    }

    if (error.response) {
      // Server responded with error status
      if (error.response.status === 404) {
        throw new NotFoundError(
          error.response.data?.detail || 'Resource not found'
        );
      }

      throw new ServiceError(
        'AI Service',
        error.response.data?.detail || error.message,
        error
      );
    }

    throw new ServiceError('AI Service', error.message, error);
  }
}

module.exports = new AiServiceClient();
