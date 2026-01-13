import { apiClient } from '../api/client';
import { AxiosError } from 'axios';
import MockAdapter from 'axios-mock-adapter';

describe('API Client', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient['client']);
    localStorage.clear();
  });

  afterEach(() => {
    mock.reset();
  });

  describe('Request Interceptor', () => {
    it('should add auth token if present in localStorage', async () => {
      localStorage.setItem('auth_token', 'test-token-123');
      mock.onGet('/test').reply(200, { success: true });

      await apiClient.get('/test');

      const request = mock.history.get[0];
      expect(request.headers?.Authorization).toBe('Bearer test-token-123');
    });

    it('should not add auth header if no token in localStorage', async () => {
      mock.onGet('/test').reply(200, { success: true });

      await apiClient.get('/test');

      const request = mock.history.get[0];
      expect(request.headers?.Authorization).toBeUndefined();
    });

    it('should include correct content-type header', async () => {
      mock.onGet('/test').reply(200, { success: true });

      await apiClient.get('/test');

      const request = mock.history.get[0];
      expect(request.headers?.['Content-Type']).toBe('application/json');
    });
  });

  describe('Response Interceptor', () => {
    it('should handle successful response', async () => {
      const mockData = { symbol: 'AAPL', price: 150 };
      mock.onGet('/test').reply(200, mockData);

      const result = await apiClient.get('/test');

      expect(result).toEqual(mockData);
    });

    it('should clear auth token on 401 response', async () => {
      localStorage.setItem('auth_token', 'test-token');
      mock.onGet('/test').reply(401, { message: 'Unauthorized' });

      try {
        await apiClient.get('/test');
      } catch (error) {
        expect(localStorage.getItem('auth_token')).toBeNull();
      }
    });

    it('should handle error responses gracefully', async () => {
      mock.onGet('/test').reply(500, { message: 'Server error' });

      await expect(apiClient.get('/test')).rejects.toThrow();
    });
  });

  describe('HTTP Methods', () => {
    it('should perform GET request', async () => {
      const mockData = { id: 1, name: 'Test' };
      mock.onGet('/data').reply(200, mockData);

      const result = await apiClient.get('/data');

      expect(result).toEqual(mockData);
    });

    it('should perform POST request with data', async () => {
      const postData = { symbol: 'AAPL' };
      const responseData = { success: true, id: 'debate-123' };
      mock.onPost('/debate').reply(200, responseData);

      const result = await apiClient.post('/debate', postData);

      expect(result).toEqual(responseData);
    });

    it('should perform PUT request with data', async () => {
      const updateData = { status: 'updated' };
      const responseData = { success: true };
      mock.onPut('/resource/1').reply(200, responseData);

      const result = await apiClient.put('/resource/1', updateData);

      expect(result).toEqual(responseData);
    });

    it('should perform DELETE request', async () => {
      mock.onDelete('/resource/1').reply(200, { success: true });

      const result = await apiClient.delete('/resource/1');

      expect(result).toEqual({ success: true });
    });

    it('should perform PATCH request', async () => {
      const patchData = { field: 'value' };
      mock.onPatch('/resource/1').reply(200, { success: true });

      const result = await apiClient.patch('/resource/1', patchData);

      expect(result).toEqual({ success: true });
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mock.onGet('/test').networkError();

      await expect(apiClient.get('/test')).rejects.toThrow();
    });

    it('should handle timeout errors', async () => {
      mock.onGet('/test').timeoutOnce();

      await expect(apiClient.get('/test')).rejects.toThrow();
    });

    it('should handle 404 Not Found', async () => {
      mock.onGet('/nonexistent').reply(404, { message: 'Not found' });

      await expect(apiClient.get('/nonexistent')).rejects.toThrow();
    });

    it('should handle 403 Forbidden', async () => {
      mock.onGet('/forbidden').reply(403, { message: 'Forbidden' });

      await expect(apiClient.get('/forbidden')).rejects.toThrow();
    });
  });
});
