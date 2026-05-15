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
  async listVolumes(limit = 100, offset = 0, cloud?: string): Promise<SuccessResponseVolume & { data: ListResponse<VolumeResponse> }> {
    const response = await apiClient.get<SuccessResponseVolume>(
      `${API_PREFIX}`,
      { params: { limit, offset, cloud } }
    )
    return response.data as any
  },

  async getVolume(volumeId: string, cloud?: string): Promise<SuccessResponseVolume> {
    const response = await apiClient.get<SuccessResponseVolume>(
      `${API_PREFIX}/${volumeId}`,
      { params: { cloud } }
    )
    return response.data
  },

  async createVolume(data: CreateVolumeRequest, cloud?: string): Promise<SuccessResponseVolume> {
    const response = await apiClient.post<SuccessResponseVolume>(
      API_PREFIX,
      data,
      { params: { cloud } }
    )
    return response.data
  },

  async deleteVolume(volumeId: string, cloud?: string): Promise<void> {
    await apiClient.delete(`${API_PREFIX}/${volumeId}`, {
      params: { cloud },
    })
  },

  async attachVolume(volumeId: string, vmId: string, cloud?: string): Promise<SuccessResponseVolume> {
    const response = await apiClient.post<SuccessResponseVolume>(
      `${API_PREFIX}/${volumeId}/attach`,
      { vm_id: vmId } as AttachVolumeRequest,
      { params: { cloud } }
    )
    return response.data
  },

  async detachVolume(volumeId: string, cloud?: string): Promise<SuccessResponseVolume> {
    const response = await apiClient.post<SuccessResponseVolume>(
      `${API_PREFIX}/${volumeId}/detach`,
      {},
      { params: { cloud } }
    )
    return response.data
  },

  // Snapshot operations
  async listSnapshots(limit = 100, offset = 0, cloud?: string): Promise<SuccessResponseSnapshot & { data: ListResponse<SnapshotResponse> }> {
    const response = await apiClient.get<SuccessResponseSnapshot>(
      `${SNAPSHOTS_PREFIX}`,
      { params: { limit, offset, cloud } }
    )
    return response.data as any
  },

  async getSnapshot(snapshotId: string, cloud?: string): Promise<SuccessResponseSnapshot> {
    const response = await apiClient.get<SuccessResponseSnapshot>(
      `${SNAPSHOTS_PREFIX}/${snapshotId}`,
      { params: { cloud } }
    )
    return response.data
  },

  async createSnapshot(data: CreateSnapshotRequest, cloud?: string): Promise<SuccessResponseSnapshot> {
    const response = await apiClient.post<SuccessResponseSnapshot>(
      SNAPSHOTS_PREFIX,
      data,
      { params: { cloud } }
    )
    return response.data
  },

  async deleteSnapshot(snapshotId: string, cloud?: string): Promise<void> {
    await apiClient.delete(`${SNAPSHOTS_PREFIX}/${snapshotId}`, {
      params: { cloud },
    })
  },
}
