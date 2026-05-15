import type { components } from '../types/api';

type NetworkResponse = components['schemas']['NetworkResponse'];
type ListNetworksResponse = components['schemas']['ListResponse_NetworkResponse_'];

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const networkService = {
  async listNetworks(limit = 100, offset = 0, cloud?: string): Promise<NetworkResponse[]> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());
    if (cloud) params.append('cloud', cloud);

    const response = await fetch(`${API_BASE}/networks?${params}`);
    if (!response.ok) throw new Error('Failed to list networks');
    const data = (await response.json()) as ListNetworksResponse;
    return data.data;
  },

  async getNetwork(networkId: string, cloud?: string): Promise<NetworkResponse> {
    const params = new URLSearchParams();
    if (cloud) params.append('cloud', cloud);

    const response = await fetch(`${API_BASE}/networks/${networkId}?${params}`);
    if (!response.ok) throw new Error('Failed to fetch network');
    const data = (await response.json()) as { data: NetworkResponse };
    return data.data;
  },
};
