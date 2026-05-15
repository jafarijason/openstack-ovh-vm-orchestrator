import type { components } from "@/types/api"
import { apiClient } from "./api"

type VolumeResponse = components["schemas"]["VolumeResponse"]
type CreateVolumeRequest = components["schemas"]["CreateVolumeRequest"]
type SnapshotResponse = components["schemas"]["SnapshotResponse"]
type CreateSnapshotRequest = components["schemas"]["CreateSnapshotRequest"]
type AttachVolumeRequest = components["schemas"]["AttachVolumeRequest"]
type SuccessResponseVolume = components["schemas"]["SuccessResponse_VolumeResponse_"]
type SuccessResponseSnapshot = components["schemas"]["SuccessResponse_SnapshotResponse_"]
type ListResponse<T> = { items: T[] }

const API_PREFIX = "/volumes"
const SNAPSHOTS_PREFIX = "/snapshots"

export const volumeService = {
  // Volume operations
  async listVolumes(limit = 100, offset = 0): Promise<SuccessResponseVolume & { data: ListResponse<VolumeResponse> }> {
    const response = await apiClient.get<SuccessResponseVolume>(
      `${API_PREFIX}?limit=${limit}&offset=${offset}`
    )
    return response.data as any
  },

  async getVolume(volumeId: string): Promise<SuccessResponseVolume> {
    const response = await apiClient.get<SuccessResponseVolume>(
      `${API_PREFIX}/${volumeId}`
    )
    return response.data
  },

  async createVolume(data: CreateVolumeRequest): Promise<SuccessResponseVolume> {
    const response = await apiClient.post<SuccessResponseVolume>(
      API_PREFIX,
      data
    )
    return response.data
  },

  async deleteVolume(volumeId: string): Promise<void> {
    await apiClient.delete(`${API_PREFIX}/${volumeId}`)
  },

  async attachVolume(volumeId: string, vmId: string): Promise<SuccessResponseVolume> {
    const response = await apiClient.post<SuccessResponseVolume>(
      `${API_PREFIX}/${volumeId}/attach`,
      { vm_id: vmId } as AttachVolumeRequest
    )
    return response.data
  },

  async detachVolume(volumeId: string): Promise<SuccessResponseVolume> {
    const response = await apiClient.post<SuccessResponseVolume>(
      `${API_PREFIX}/${volumeId}/detach`,
      {}
    )
    return response.data
  },

  // Snapshot operations
  async listSnapshots(limit = 100, offset = 0): Promise<SuccessResponseSnapshot & { data: ListResponse<SnapshotResponse> }> {
    const response = await apiClient.get<SuccessResponseSnapshot>(
      `${SNAPSHOTS_PREFIX}?limit=${limit}&offset=${offset}`
    )
    return response.data as any
  },

  async getSnapshot(snapshotId: string): Promise<SuccessResponseSnapshot> {
    const response = await apiClient.get<SuccessResponseSnapshot>(
      `${SNAPSHOTS_PREFIX}/${snapshotId}`
    )
    return response.data
  },

  async createSnapshot(data: CreateSnapshotRequest): Promise<SuccessResponseSnapshot> {
    const response = await apiClient.post<SuccessResponseSnapshot>(
      SNAPSHOTS_PREFIX,
      data
    )
    return response.data
  },

  async deleteSnapshot(snapshotId: string): Promise<void> {
    await apiClient.delete(`${SNAPSHOTS_PREFIX}/${snapshotId}`)
  },
}
