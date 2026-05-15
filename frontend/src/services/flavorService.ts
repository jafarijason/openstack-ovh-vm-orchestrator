import type { components } from "@/types/api"
import { apiClient } from "./api"

type ListResponseFlavor = components["schemas"]["ListResponse_FlavorResponse_"]

const API_PREFIX = "/flavors"

export const flavorService = {
  async listFlavors(limit = 100, offset = 0, cloud?: string): Promise<ListResponseFlavor> {
    const response = await apiClient.get<ListResponseFlavor>(
      `${API_PREFIX}`,
      { params: { limit, offset, cloud } }
    )
    return response.data
  },
}
