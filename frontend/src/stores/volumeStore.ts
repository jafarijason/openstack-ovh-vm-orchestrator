import { create } from "zustand"
import type { components } from "@/types/api"

type VolumeResponse = components["schemas"]["VolumeResponse"]

interface VolumeState {
  volumes: VolumeResponse[]
  loading: boolean
  error: string | null
  setVolumes: (volumes: VolumeResponse[]) => void
  addVolume: (volume: VolumeResponse) => void
  updateVolume: (volume: VolumeResponse) => void
  removeVolume: (volumeId: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
  reset: () => void
}

export const useVolumeStore = create<VolumeState>((set) => ({
  volumes: [],
  loading: false,
  error: null,

  setVolumes: (volumes) => set({ volumes }),

  addVolume: (volume) =>
    set((state) => ({
      volumes: [volume, ...state.volumes],
    })),

  updateVolume: (volume) =>
    set((state) => ({
      volumes: state.volumes.map((v) => (v.id === volume.id ? volume : v)),
    })),

  removeVolume: (volumeId) =>
    set((state) => ({
      volumes: state.volumes.filter((v) => v.id !== volumeId),
    })),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  clearError: () => set({ error: null }),

  reset: () =>
    set({
      volumes: [],
      loading: false,
      error: null,
    }),
}))
