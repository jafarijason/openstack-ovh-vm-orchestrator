import { apiClient } from './api';
import type { components } from '../types/api';

type VMResponse = components['schemas']['VMResponse'];
type CreateVMRequest = components['schemas']['CreateVMRequest'];
type SuccessResponseVM = components['schemas']['SuccessResponse_VMResponse_'];
type VMActionRequest = components['schemas']['VMActionRequest'];

interface VMListResponse {
  success: boolean;
  data: VMResponse[];
  pagination?: {
    limit: number;
    offset: number;
    total: number;
  };
}

export const vmService = {
  /**
   * List all VMs with pagination
   */
  async listVMs(limit = 100, offset = 0, cloud?: string): Promise<VMListResponse> {
    const response = await apiClient.get('/vms', {
      params: { limit, offset, cloud },
    });
    return response.data;
  },

  /**
   * Get a specific VM by ID
   */
  async getVM(vmId: string, cloud?: string): Promise<SuccessResponseVM> {
    const response = await apiClient.get(`/vms/${vmId}`, {
      params: { cloud },
    });
    return response.data;
  },

  /**
   * Create a new VM
   */
  async createVM(data: CreateVMRequest, cloud?: string): Promise<SuccessResponseVM> {
    const response = await apiClient.post('/vms', data, {
      params: { cloud },
    });
    return response.data;
  },

  /**
   * Delete a VM
   */
  async deleteVM(vmId: string, cloud?: string): Promise<void> {
    await apiClient.delete(`/vms/${vmId}`, {
      params: { cloud },
    });
  },

  /**
   * Perform an action on a VM (start, stop, reboot)
   */
  async performVMAction(
    vmId: string,
    action: 'start' | 'stop' | 'reboot',
    cloud?: string
  ): Promise<components['schemas']['SuccessResponse_VMActionResponse_']> {
    const response = await apiClient.post(
      `/vms/${vmId}/action`,
      { action } as VMActionRequest,
      {
        params: { cloud },
      }
    );
    return response.data;
  },

  /**
   * Start a VM
   */
  async startVM(vmId: string, cloud?: string): Promise<components['schemas']['SuccessResponse_VMActionResponse_']> {
    return this.performVMAction(vmId, 'start', cloud);
  },

  /**
   * Stop a VM
   */
  async stopVM(vmId: string, cloud?: string): Promise<components['schemas']['SuccessResponse_VMActionResponse_']> {
    return this.performVMAction(vmId, 'stop', cloud);
  },

  /**
   * Reboot a VM
   */
  async rebootVM(vmId: string, cloud?: string): Promise<components['schemas']['SuccessResponse_VMActionResponse_']> {
    return this.performVMAction(vmId, 'reboot', cloud);
  },
};
