import { create } from 'zustand';
import { cloudService } from '../services/cloudService';

interface CloudState {
  activeClouds: string[];
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
      set({
        activeClouds: response.data.clouds,
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

  setError: (error: string | null) => {
    set({ error });
  },

  clearError: () => {
    set({ error: null });
  },
}));
