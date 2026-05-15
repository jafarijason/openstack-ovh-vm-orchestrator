import { create } from 'zustand';
import { cloudService } from '../services/cloudService';

const STORAGE_KEY = 'orchestrator_selected_cloud';

export interface Cloud {
  name: string;
  type: 'mock' | 'openstack' | 'other';
  authenticated: boolean;
  available?: boolean;
  error?: string | null;
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
  loadPersistedCloud: () => void;
}

// Helper functions for localStorage
const saveCloudToStorage = (cloudName: string) => {
  try {
    localStorage.setItem(STORAGE_KEY, cloudName);
  } catch (e) {
    console.warn('Failed to save cloud to localStorage:', e);
  }
};

const loadCloudFromStorage = (): string | null => {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch (e) {
    console.warn('Failed to load cloud from localStorage:', e);
    return null;
  }
};

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
      const cloudsArray: Cloud[] = Object.entries(response.clouds || {}).map(
        ([name, info]) => ({
          name,
          type: info.type || 'other',
          authenticated: info.authenticated || false,
          available: info.available !== false, // Default to true if not specified
          error: info.error || null,
        })
      );
      
      // Get persisted cloud or use server's active cloud
      const persistedCloud = loadCloudFromStorage();
      const activeCloud = persistedCloud || response.active_cloud;
      
      set({
        activeClouds: cloudsArray,
        activeCloud,
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
    // Save to localStorage when switching clouds
    saveCloudToStorage(cloudName);
    set({ activeCloud: cloudName, error: null });
  },

  loadPersistedCloud: () => {
    const persistedCloud = loadCloudFromStorage();
    if (persistedCloud) {
      set({ activeCloud: persistedCloud });
    }
  },

  setError: (error: string | null) => {
    set({ error });
  },

  clearError: () => {
    set({ error: null });
  },
}));
