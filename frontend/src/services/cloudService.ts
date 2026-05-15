import { apiClient } from './api';

interface CloudStatus {
  success: boolean;
  data: {
    clouds: string[];
    active_cloud: string;
  };
}

interface HealthStatus {
  status: string;
  timestamp: string;
  version?: string;
}

export const cloudService = {
  /**
   * Get status of all configured clouds
   */
  async getCloudsStatus(): Promise<CloudStatus> {
    const response = await apiClient.get('/clouds');
    return response.data;
  },

  /**
   * Health check to verify API is running
   */
  async healthCheck(): Promise<HealthStatus> {
    const response = await apiClient.get('/health');
    return response.data;
  },

  /**
   * Hello world endpoint
   */
  async hello(): Promise<{ message: string }> {
    const response = await apiClient.get('/');
    return response.data;
  },
};
