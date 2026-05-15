import React, { useEffect, useState } from "react"
import type { components } from "@/types/api"
import { imageService } from "@/services/imageService"
import { useCloudStore } from "@/stores/cloudStore"
import { LoadingSpinner } from "@/components/common/LoadingSpinner"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { MetadataViewer } from "@/components/common/MetadataViewer"

type ImageResponse = components["schemas"]["ImageResponse"]

export const ImageList: React.FC = () => {
  const { activeCloud, activeClouds } = useCloudStore()
  const [images, setImages] = useState<ImageResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedImageId, setExpandedImageId] = useState<string | null>(null)
  const loadImages = async (cloud: string) => {
    try {
      setLoading(true)
      setImages([])
      setError(null)
      const response = await imageService.listImages(1000, 0, cloud)
      setImages(response.data || [])
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Failed to load images"
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (activeClouds.length > 0 && activeCloud) {
      loadImages(activeCloud)
    }
  }, [activeCloud, activeClouds])

  const formatBytes = (bytes: number | null | undefined): string => {
    if (!bytes) return "N/A"
    const gb = bytes / (1024 * 1024 * 1024)
    return gb.toFixed(2) + " GB"
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ACTIVE":
        return "text-green-600 bg-green-50"
      case "QUEUED":
      case "SAVING":
        return "text-blue-600 bg-blue-50"
      case "DELETED":
      case "KILLED":
        return "text-red-600 bg-red-50"
      default:
        return "text-gray-600 bg-gray-50"
    }
  }

  if (loading && images.length === 0) {
    return <LoadingSpinner />
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Images</h1>
          <p className="text-gray-600">
            Available images for your cloud ({activeCloud})
          </p>
        </div>

        {/* Error Alert */}
        {error && <ErrorAlert message={error} />}



        {/* Images Table */}
         <div className="bg-white rounded-lg shadow overflow-hidden">
           <div className="overflow-x-auto">
             <table className="w-full">
               <thead className="bg-gray-100 border-b border-gray-200">
                 <tr>
                   <th className="w-8 px-4 py-3"></th>
                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                     Name
                   </th>
                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                     Status
                   </th>
                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                     Size
                   </th>
                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                     Format
                   </th>
                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                     Min Disk
                   </th>
                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                     Min RAM
                   </th>
                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                     Access
                   </th>
                 </tr>
               </thead>
               <tbody className="divide-y divide-gray-200">
                 {images.length > 0 ? (
                   images.map((image) => (
                     <React.Fragment key={image.id}>
                       <tr
                         className="hover:bg-gray-50 cursor-pointer"
                         onClick={() =>
                           setExpandedImageId(
                             expandedImageId === image.id ? null : image.id
                           )
                         }
                       >
                         <td className="px-4 py-4 text-center">
                           <span className="text-gray-400">
                             {expandedImageId === image.id ? '▼' : '▶'}
                           </span>
                         </td>
                         <td className="px-6 py-4">
                           <div>
                             <p className="text-sm font-medium text-gray-900">
                               {image.name}
                             </p>
                             <p className="text-xs text-gray-500 break-all">
                               {image.id}
                             </p>
                           </div>
                         </td>
                         <td className="px-6 py-4">
                           <span
                             className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                               image.status
                             )}`}
                           >
                             {image.status}
                           </span>
                         </td>
                         <td className="px-6 py-4 text-sm text-gray-600">
                           {formatBytes(image.size_bytes)}
                         </td>
                         <td className="px-6 py-4 text-sm text-gray-600">
                           <div>
                             <p>{image.disk_format || "N/A"}</p>
                             <p className="text-xs text-gray-500">
                               {image.container_format || "N/A"}
                             </p>
                           </div>
                         </td>
                         <td className="px-6 py-4 text-sm text-gray-600">
                           {image.min_disk_gb || 0} GB
                         </td>
                         <td className="px-6 py-4 text-sm text-gray-600">
                           {image.min_ram_mb || 0} MB
                         </td>
                         <td className="px-6 py-4 text-sm">
                           <div className="flex gap-2">
                             {image.is_public ? (
                               <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                                 Public
                               </span>
                             ) : (
                               <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                                 Private
                               </span>
                             )}
                             {image.is_protected && (
                               <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded">
                                 Protected
                               </span>
                             )}
                           </div>
                         </td>
                       </tr>
                       {expandedImageId === image.id && (
                         <tr className="bg-gray-50">
                           <td colSpan={8} className="px-6 py-4">
                             <MetadataViewer
                               metadata={image.metadata}
                               name={`Metadata - ${image.name}`}
                             />
                           </td>
                         </tr>
                       )}
                     </React.Fragment>
                   ))
                 ) : (
                   <tr>
                     <td
                       colSpan={8}
                       className="px-6 py-8 text-center text-gray-500"
                     >
                       No images found
                     </td>
                   </tr>
                 )}
               </tbody>
             </table>
           </div>
         </div>


      </div>
    </div>
  )
}
