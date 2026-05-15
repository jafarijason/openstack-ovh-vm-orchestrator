import { create } from "zustand"
import type { components } from "@/types/api"

type SnapshotResponse = components["schemas"]["SnapshotResponse"]

interface SnapshotState {
  snapshots: SnapshotResponse[]
  loading: boolean
  error: string | null
  setSnapshots: (snapshots: SnapshotResponse[]) => void
  addSnapshot: (snapshot: SnapshotResponse) => void
  updateSnapshot: (snapshot: SnapshotResponse) => void
  removeSnapshot: (snapshotId: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
  reset: () => void
}

export const useSnapshotStore = create<SnapshotState>((set) => ({
  snapshots: [],
  loading: false,
  error: null,

  setSnapshots: (snapshots) => set({ snapshots }),

  addSnapshot: (snapshot) =>
    set((state) => ({
      snapshots: [snapshot, ...state.snapshots],
    })),

  updateSnapshot: (snapshot) =>
    set((state) => ({
      snapshots: state.snapshots.map((s) =>
        s.id === snapshot.id ? snapshot : s
      ),
    })),

  removeSnapshot: (snapshotId) =>
    set((state) => ({
      snapshots: state.snapshots.filter((s) => s.id !== snapshotId),
    })),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  clearError: () => set({ error: null }),

  reset: () =>
    set({
      snapshots: [],
      loading: false,
      error: null,
    }),
}))
