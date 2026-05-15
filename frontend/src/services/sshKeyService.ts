import type { components } from "@/types/api"
import { apiClient } from "./api"

type ListResponseSSHKey = components["schemas"]["ListResponse_SSHKeyResponse_"]

const API_PREFIX = "/ssh-keys"

export const sshKeyService = {
  async listSSHKeys(limit = 100, offset = 0, cloud?: string): Promise<ListResponseSSHKey> {
    const response = await apiClient.get<ListResponseSSHKey>(
      `${API_PREFIX}`,
      { params: { limit, offset, cloud } }
    )
    return response.data
  },
}
