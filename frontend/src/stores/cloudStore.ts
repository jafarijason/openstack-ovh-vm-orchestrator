import { create } from 'zustand';
import { cloudService } from '../services/cloudService';

export interface Cloud {
  name: string;
  type: 'mock' | 'openstack' | 'other';
  authenticated: boolean;
}

interface CloudState {
  activeClouds: Cloud[];
  activeCloud: string;
  healthStatus: {
    status: string;
    timestamp: string;
    version?: string;
  } | null;
  loading: boolean;
  error: string | null;

  // Actions
  fetchCloudsStatus: () => Promise<void>;
  checkHealth: () => Promise<void>;
  setError: (error: string | null) => void;
  clearError: () => void;
  switchCloud: (cloudName: string) => void;
}

export const useCloudStore = create<CloudState>((set) => ({
  activeClouds: [],
  activeCloud: '',
  healthStatus: null,
  loading: false,
  error: null,

  fetchCloudsStatus: async () => {
    set({ loading: true, error: null });
    try {
      const response = await cloudService.getCloudsStatus();
      // Convert clouds object to array format
      const cloudsArray: Cloud[] = Object.entries(response.data.clouds || {}).map(
        ([name, info]: [string, any]) => ({
          name,
          type: info.type || 'other',
          authenticated: info.authenticated || false,
        })
      );
      set({
        activeClouds: cloudsArray,
        activeCloud: response.data.active_cloud,
        loading: false,
      });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to fetch clouds status';
      set({ error: errorMessage, loading: false });
    }
  },

  checkHealth: async () => {
    try {
      const health = await cloudService.healthCheck();
      set({ healthStatus: health });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Health check failed';
      set({ error: errorMessage });
    }
  },

  switchCloud: (cloudName: string) => {
    set({ activeCloud: cloudName, error: null });
  },

  setError: (error: string | null) => {
    set({ error });
  },

  clearError: () => {
    set({ error: null });
  },
}));
