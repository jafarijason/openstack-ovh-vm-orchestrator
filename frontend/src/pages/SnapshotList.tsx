import React, { useEffect, useState } from "react"
import type { components } from "@/types/api"
import { volumeService } from "@/services/volumeService"
import { useCloudStore } from "@/stores/cloudStore"
import { LoadingSpinner } from "@/components/common/LoadingSpinner"
import { ErrorAlert } from "@/components/common/ErrorAlert"
import { MetadataViewer } from "@/components/common/MetadataViewer"

type SnapshotResponse = components["schemas"]["SnapshotResponse"]
type CreateSnapshotRequest = components["schemas"]["CreateSnapshotRequest"]

interface FormData {
  volume_id: string
  name: string
  description: string
}

export const SnapshotList: React.FC = () => {
  const { activeCloud, activeClouds } = useCloudStore()
  const [snapshots, setSnapshots] = useState<SnapshotResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState<FormData>({
    volume_id: "",
    name: "",
    description: "",
  })
  const [submitting, setSubmitting] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set())
  const [expandedSnapshotId, setExpandedSnapshotId] = useState<string | null>(null)

   const loadSnapshots = async (cloud: string) => {
     try {
       setLoading(true)
       setSnapshots([]); // Clear old data immediately when cloud changes
       setError(null)
       const response = await volumeService.listSnapshots(100, 0, cloud)
       setSnapshots(response.data.items || [])
     } catch (err) {
       setError(err instanceof Error ? err.message : "Failed to load snapshots")
     } finally {
       setLoading(false)
     }
   }

   useEffect(() => {
     // Only load when we have clouds fetched and activeCloud is set
     if (activeClouds.length > 0 && activeCloud) {
       loadSnapshots(activeCloud)
     }
   }, [activeCloud, activeClouds])

  const handleCreateSnapshot = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.volume_id.trim()) {
      setError("Please select a volume")
      return
    }
    if (!formData.name.trim()) {
      setError("Snapshot name is required")
      return
    }

    try {
      setSubmitting(true)
      setError(null)
      const createData: CreateSnapshotRequest = {
        volume_id: formData.volume_id,
        name: formData.name,
        description: formData.description || undefined,
      }
       await volumeService.createSnapshot(createData, activeCloud)
       setShowCreateForm(false)
       setFormData({ volume_id: "", name: "", description: "" })
       await loadSnapshots(activeCloud)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create snapshot")
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeleteSnapshot = async (snapshotId: string) => {
    try {
      setDeletingIds(new Set([...deletingIds, snapshotId]))
      setError(null)
      await volumeService.deleteSnapshot(snapshotId, activeCloud)
      setSnapshots(snapshots.filter((s) => s.id !== snapshotId))
      setDeleteConfirm(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete snapshot")
    } finally {
      setDeletingIds(new Set([...deletingIds].filter((id) => id !== snapshotId)))
    }
  }

  const getStatusColor = (status: string) => {
    const statusLower = status.toLowerCase()
    if (statusLower === "available") return "bg-green-100 text-green-800"
    if (statusLower === "creating") return "bg-yellow-100 text-yellow-800"
    if (statusLower === "deleting") return "bg-red-100 text-red-800"
    if (statusLower === "error") return "bg-red-100 text-red-800"
    return "bg-gray-100 text-gray-800"
  }

  const getStatusIcon = (status: string) => {
    const statusLower = status.toLowerCase()
    if (statusLower === "available")
      return (
        <svg
          className="w-5 h-5 text-green-600"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clipRule="evenodd"
          />
        </svg>
      )
    return (
      <svg
        className="w-5 h-5 text-gray-400 animate-spin"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M13 10V3L4 14h7v7l9-11h-7z"
        />
      </svg>
    )
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Snapshots</h1>
          <p className="text-gray-600 mt-1">
            Create and manage volume snapshots
          </p>
        </div>
        <div className="flex justify-center items-center min-h-96">
          <LoadingSpinner />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Snapshots</h1>
          <p className="text-gray-600 mt-1">
            Create and manage volume snapshots
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Create Snapshot
        </button>
      </div>

      {/* Error Alert */}
      {error && <ErrorAlert message={error} />}

      {/* Create Snapshot Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">
                Create Snapshot
              </h2>
            </div>
            <form onSubmit={handleCreateSnapshot} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Snapshot Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="my-snapshot"
                  disabled={submitting}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Volume ID *
                </label>
                <input
                  type="text"
                  value={formData.volume_id}
                  onChange={(e) =>
                    setFormData({ ...formData, volume_id: e.target.value })
                  }
                  placeholder="volume-id"
                  disabled={submitting}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
                <p className="text-xs text-gray-500 mt-1">
                  ID of the volume to snapshot
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder="Optional description"
                  rows={3}
                  disabled={submitting}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  disabled={submitting}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {submitting ? "Creating..." : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Snapshots Grid */}
      {snapshots.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg
            className="w-16 h-16 text-gray-400 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <p className="text-gray-600 text-lg">No snapshots yet</p>
          <p className="text-gray-500 text-sm mt-1">
            Create a snapshot to protect your volume data
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {snapshots.map((snapshot) => (
            <div
              key={snapshot.id}
              className="bg-white rounded-lg shadow hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900">
                      {snapshot.name}
                    </h3>
                    <p className="text-sm text-gray-500 font-mono mt-1">
                      {snapshot.id}
                    </p>
                  </div>
                </div>

                {/* Status Badge */}
                <div className="mb-4">
                  <span
                    className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(snapshot.status)}`}
                  >
                    {getStatusIcon(snapshot.status)}
                    {snapshot.status}
                  </span>
                </div>

                {/* Details */}
                <div className="space-y-2 mb-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Volume ID:</span>
                    <span className="font-medium text-gray-900 font-mono text-xs">
                      {snapshot.volume_id.substring(0, 8)}...
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Size:</span>
                    <span className="font-medium text-gray-900">
                      {snapshot.size_gb} GB
                    </span>
                  </div>
                  {snapshot.description && (
                    <div className="pt-2">
                      <p className="text-gray-600">{snapshot.description}</p>
                    </div>
                  )}
                  {snapshot.created_at && (
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Created:</span>
                      <span>
                        {new Date(snapshot.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                {/* Delete Confirmation */}
                {deleteConfirm === snapshot.id && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-800 mb-3">
                      Are you sure? This action cannot be undone.
                    </p>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setDeleteConfirm(null)}
                        disabled={deletingIds.has(snapshot.id)}
                        className="flex-1 text-sm px-3 py-1 border border-red-300 text-red-700 rounded hover:bg-red-50 transition-colors disabled:opacity-50"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleDeleteSnapshot(snapshot.id)}
                        disabled={deletingIds.has(snapshot.id)}
                        className="flex-1 text-sm px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors disabled:opacity-50"
                      >
                        {deletingIds.has(snapshot.id) ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                  </div>
                )}

                {/* Metadata Viewer */}
                {expandedSnapshotId === snapshot.id && (
                  <div className="mb-4 pt-4 border-t border-gray-200">
                    <MetadataViewer
                      metadata={snapshot.metadata}
                      name={`Metadata - ${snapshot.name}`}
                    />
                  </div>
                )}

                {/* Actions */}
                {deleteConfirm !== snapshot.id && (
                  <div className="flex gap-2 pt-4 border-t border-gray-200">
                    <button
                      onClick={() =>
                        setExpandedSnapshotId(
                          expandedSnapshotId === snapshot.id ? null : snapshot.id
                        )
                      }
                      className="flex-1 text-sm px-3 py-2 text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-50 font-medium"
                    >
                      {expandedSnapshotId === snapshot.id
                        ? "Hide Metadata"
                        : "View Metadata"}
                    </button>
                    <button
                      onClick={() => setDeleteConfirm(snapshot.id)}
                      disabled={deletingIds.has(snapshot.id)}
                      className="flex-1 text-sm px-3 py-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50 font-medium"
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SnapshotList
