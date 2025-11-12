import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003';

export const fetchDebate = async (symbol: string) => {
  // Example: call the backend agentic service to start a debate
  const response = await axios.post(`${API_BASE_URL}/api/v1/debate`, { symbol });
  return response.data;
};
