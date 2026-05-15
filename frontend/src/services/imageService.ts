import type { components } from "@/types/api"
import { apiClient } from "./api"

type ListResponseImage = components["schemas"]["ListResponse_ImageResponse_"]

const API_PREFIX = "/images"

export const imageService = {
  async listImages(limit = 100, offset = 0, cloud?: string): Promise<ListResponseImage> {
    const response = await apiClient.get<ListResponseImage>(
      `${API_PREFIX}`,
      { params: { limit, offset, cloud } }
    )
    return response.data
  },
}
