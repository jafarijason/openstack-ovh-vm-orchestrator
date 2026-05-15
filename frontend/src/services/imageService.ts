import type { components } from "@/types/api"
import { apiClient } from "./api"

type ImageResponse = components["schemas"]["ImageResponse"]
type ListResponse<T> = { items: T[] }
type SuccessResponseImage = { success: boolean; data: ImageResponse[]; pagination: { total: number; page: number; per_page: number; pages: number }; message?: string }

const API_PREFIX = "/images"

export const imageService = {
  async listImages(limit = 100, offset = 0, cloud?: string): Promise<SuccessResponseImage> {
    const response = await apiClient.get<SuccessResponseImage>(
      `${API_PREFIX}`,
      { params: { limit, offset, cloud } }
    )
    return response.data
  },
}
