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
  async listVMs(limit = 100, offset = 0): Promise<VMListResponse> {
    const response = await apiClient.get('/vms', {
      params: { limit, offset },
    });
    return response.data;
  },

  /**
   * Get a specific VM by ID
   */
  async getVM(vmId: string): Promise<SuccessResponseVM> {
    const response = await apiClient.get(`/vms/${vmId}`);
    return response.data;
  },

  /**
   * Create a new VM
   */
  async createVM(data: CreateVMRequest): Promise<SuccessResponseVM> {
    const response = await apiClient.post('/vms', data);
    return response.data;
  },

  /**
   * Delete a VM
   */
  async deleteVM(vmId: string): Promise<void> {
    await apiClient.delete(`/vms/${vmId}`);
  },

  /**
   * Perform an action on a VM (start, stop, reboot)
   */
  async performVMAction(
    vmId: string,
    action: 'start' | 'stop' | 'reboot'
  ): Promise<components['schemas']['SuccessResponse_VMActionResponse_']> {
    const response = await apiClient.post(`/vms/${vmId}/action`, {
      action,
    } as VMActionRequest);
    return response.data;
  },

  /**
   * Start a VM
   */
  async startVM(vmId: string): Promise<components['schemas']['SuccessResponse_VMActionResponse_']> {
    return this.performVMAction(vmId, 'start');
  },

  /**
   * Stop a VM
   */
  async stopVM(vmId: string): Promise<components['schemas']['SuccessResponse_VMActionResponse_']> {
    return this.performVMAction(vmId, 'stop');
  },

  /**
   * Reboot a VM
   */
  async rebootVM(vmId: string): Promise<components['schemas']['SuccessResponse_VMActionResponse_']> {
    return this.performVMAction(vmId, 'reboot');
  },
};
