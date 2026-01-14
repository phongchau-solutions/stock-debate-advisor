/**
 * Service client for Data Service communication
 */

const axios = require('axios');
const config = require('../config');
const logger = require('../utils/logger');
const {
  ServiceError,
  TimeoutError,
  NotFoundError,
} = require('../utils/errors');

class DataServiceClient {
  constructor() {
    this.baseURL = config.services.dataService.url;
    this.timeout = config.services.dataService.timeout;
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: this.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Get company information
   * @param {string} symbol - Stock symbol
   * @returns {Promise<object>} Company information
   */
  async getCompany(symbol) {
    try {
      logger.debug(`Fetching company info for ${symbol}`);
      const response = await this.client.get(`/api/v1/company/${symbol}`);
      logger.debug(`Company info fetched for ${symbol}`);
      // Extract data from v3 response format: {status, data}
      return response.data.data || response.data;
    } catch (error) {
      this.handleError(error, 'getCompany');
    }
  }

  /**
   * Get all stocks list
   * @returns {Promise<object>} List of all stocks
   */
  async getStocks() {
    try {
      logger.debug('Fetching all stocks');
      const response = await this.client.get('/api/v1/stocks/list');
      logger.debug('Stocks list fetched');
      return response.data.data || response.data;
    } catch (error) {
      this.handleError(error, 'getStocks');
    }
  }

  /**
   * Search companies
   * @param {string} query - Search query
   * @param {number} limit - Number of results
   * @returns {Promise<object>} Search results
   */
  async searchCompanies(query, limit = 10) {
    try {
      logger.debug(`Searching companies for: ${query}`);
      const response = await this.client.get(
        `/api/v1/stocks/search?query=${encodeURIComponent(query)}&limit=${limit}`
      );
      logger.debug(`Search results for: ${query}`);
      return response.data.data || response.data;
    } catch (error) {
      this.handleError(error, 'searchCompanies');
    }
  }

  /**
   * Get all financial reports
   * @param {string} symbol - Stock symbol
   * @returns {Promise<object>} Financial reports
   */
  async getFinancials(symbol) {
    try {
      logger.debug(`Fetching financials for ${symbol}`);
      const response = await this.client.get(`/api/v1/financials/${symbol}`);
      logger.debug(`Financials fetched for ${symbol}`);
      return response.data.data || response.data;
    } catch (error) {
      this.handleError(error, 'getFinancials');
    }
  }

  /**
   * Get quarterly financial reports
   * @param {string} symbol - Stock symbol
   * @param {number} limit - Number of reports to fetch
   * @returns {Promise<object>} Financial reports
   */
  async getQuarterlyReports(symbol, limit = 8) {
    try {
      logger.debug(`Fetching quarterly reports for ${symbol}`);
      const response = await this.client.get(
        `/api/v1/financials/quarterly/${symbol}?limit=${limit}`
      );
      logger.debug(`Quarterly reports fetched for ${symbol}`);
      return response.data.data || response.data;
    } catch (error) {
      this.handleError(error, 'getQuarterlyReports');
    }
  }

  /**
   * Get annual financial reports
   * @param {string} symbol - Stock symbol
   * @param {number} limit - Number of reports to fetch
   * @returns {Promise<object>} Financial reports
   */
  async getAnnualReports(symbol, limit = 5) {
    try {
      logger.debug(`Fetching annual reports for ${symbol}`);
      const response = await this.client.get(
        `/api/v1/financials/annual/${symbol}?limit=${limit}`
      );
      logger.debug(`Annual reports fetched for ${symbol}`);
      return response.data.data || response.data;
    } catch (error) {
      this.handleError(error, 'getAnnualReports');
    }
  }

  /**
   * Get financial metrics
   * @param {string} symbol - Stock symbol
   * @returns {Promise<object>} Financial metrics
   */
  async getFinancialMetrics(symbol) {
    try {
      logger.debug(`Fetching financial metrics for ${symbol}`);
      const response = await this.client.get(
        `/api/v1/financials/metrics/${symbol}`
      );
      logger.debug(`Financial metrics fetched for ${symbol}`);
      return response.data.data || response.data;
    } catch (error) {
      this.handleError(error, 'getFinancialMetrics');
    }
  }

  /**
   * Get dividend information
   * @param {string} symbol - Stock symbol
   * @returns {Promise<object>} Dividend data
   */
  async getDividends(symbol) {
    try {
      logger.debug(`Fetching dividends for ${symbol}`);
      const response = await this.client.get(`/api/v1/dividends/${symbol}`);
      logger.debug(`Dividends fetched for ${symbol}`);
      return response.data.data || response.data;
    } catch (error) {
      this.handleError(error, 'getDividends');
    }
  }

  /**
   * Get stock splits
   * @param {string} symbol - Stock symbol
   * @returns {Promise<object>} Stock split data
   */
  async getStockSplits(symbol) {
    try {
      logger.debug(`Fetching stock splits for ${symbol}`);
      const response = await this.client.get(`/api/v1/splits/${symbol}`);
      logger.debug(`Stock splits fetched for ${symbol}`);
      return response.data.data || response.data;
    } catch (error) {
      this.handleError(error, 'getStockSplits');
    }
  }

  /**
   * Get price data
   * @param {string} symbol - Stock symbol
   * @param {number} limit - Number of days to fetch
   * @returns {Promise<object>} Price data
   */
  async getPriceData(symbol, limit = 30) {
    try {
      logger.debug(`Fetching price data for ${symbol} (${limit} records)`);
      const response = await this.client.get(
        `/api/v1/prices/${symbol}?limit=${limit}`
      );
      logger.debug(`Price data fetched for ${symbol}`);
      return response.data.data || response.data;
    } catch (error) {
      this.handleError(error, 'getPriceData');
    }
  }

  /**
   * Get news data
   * @param {string} symbol - Stock symbol
   * @returns {Promise<object>} News data
   */
  async getNews(symbol) {
    try {
      logger.debug(`Fetching news for ${symbol}`);
      const response = await this.client.get(`/api/v1/news/${symbol}`);
      logger.debug(`News fetched for ${symbol}`);
      return response.data.data || response.data;
    } catch (error) {
      this.handleError(error, 'getNews');
    }
  }

  /**
   * Get complete stock data (all info, financials, and prices)
   * @param {string} symbol - Stock symbol
   * @returns {Promise<object>} Complete stock data
   */
  async getFullStockData(symbol) {
    try {
      logger.debug(`Fetching full stock data for ${symbol}`);
      const response = await this.client.get(`/api/v1/stock/${symbol}/full`);
      logger.debug(`Full stock data fetched for ${symbol}`);
      return response.data.data || response.data;
    } catch (error) {
      this.handleError(error, 'getFullStockData');
    }
  }

  /**
   * Handle errors from data service
   * @private
   */
  handleError(error, operation) {
    logger.error(`Data Service error in ${operation}: ${error.message}`);

    if (error.code === 'ECONNABORTED') {
      throw new TimeoutError('Data Service');
    }

    if (error.response) {
      // Server responded with error status
      if (error.response.status === 404) {
        throw new NotFoundError(
          error.response.data?.detail || 'Resource not found'
        );
      }

      throw new ServiceError(
        'Data Service',
        error.response.data?.detail || error.message,
        error
      );
    }

    throw new ServiceError('Data Service', error.message, error);
  }
}

module.exports = new DataServiceClient();
