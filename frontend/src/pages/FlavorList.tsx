import React, { useEffect, useState } from 'react';
import { flavorService } from '../services/flavorService';
import { useCloudStore } from '../stores/cloudStore';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { MetadataViewer } from '../components/common/MetadataViewer';
import type { components } from '../types/api';

type FlavorResponse = components['schemas']['FlavorResponse'];

export const FlavorList: React.FC = () => {
  const { activeCloud, activeClouds } = useCloudStore();
  const [flavors, setFlavors] = useState<FlavorResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedFlavorId, setExpandedFlavorId] = useState<string | null>(null);

  const loadFlavors = async (cloud: string) => {
    try {
      setLoading(true);
      setFlavors([]);
      const response = await flavorService.listFlavors(100, 0, cloud);
      setFlavors(response.data);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load flavors';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeClouds.length > 0 && activeCloud) {
      loadFlavors(activeCloud);
    }
  }, [activeCloud, activeClouds]);

  const formatBytes = (mb: number | null | undefined): string => {
    if (!mb) return '-';
    if (mb >= 1024) return `${(mb / 1024).toFixed(1)} GB`;
    return `${mb} MB`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Flavors</h1>
        <p className="text-gray-600 mt-1">
          {flavors.length} flavor{flavors.length !== 1 ? 's' : ''} available
        </p>
      </div>

      {error && <ErrorAlert message={error} onClose={() => setError(null)} />}

      {loading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner message="Loading flavors..." />
        </div>
      ) : flavors.length === 0 ? (
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
              d="M9 3v2m6-2v2m-9 4v10a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2zm0 0a2 2 0 012-2h10a2 2 0 012 2"
            />
          </svg>
          <p className="text-gray-600 text-lg">No flavors found</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="w-8 px-4 py-3"></th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    vCPUs
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    RAM
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Disk
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Swap
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Public
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {flavors.map((flavor) => (
                  <React.Fragment key={flavor.id}>
                    <tr
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => setExpandedFlavorId(expandedFlavorId === flavor.id ? null : flavor.id)}
                    >
                      <td className="px-4 py-4 text-center">
                        <span className="text-gray-400">
                          {expandedFlavorId === flavor.id ? '▼' : '▶'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {flavor.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {flavor.vcpus || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatBytes(flavor.ram_mb)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {flavor.disk_gb ? `${flavor.disk_gb} GB` : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatBytes(flavor.swap_mb)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            flavor.is_public
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {flavor.is_public ? 'Yes' : 'No'}
                        </span>
                      </td>
                    </tr>
                    {expandedFlavorId === flavor.id && (
                      <>
                        <tr className="bg-gray-100 border-b border-gray-200">
                          <td colSpan={7} className="px-6 py-4">
                            <div className="grid grid-cols-2 gap-8">
                              {/* Basic Info */}
                              <div>
                                <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                                  ID
                                </h4>
                                <p className="text-sm font-mono text-gray-900 break-all">{flavor.id}</p>
                              </div>
                              {/* Description */}
                              <div>
                                <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                                  Description
                                </h4>
                                <p className="text-sm text-gray-900">
                                  {flavor.description || 'N/A'}
                                </p>
                              </div>
                            </div>
                            <div className="grid grid-cols-4 gap-4 mt-4">
                              {/* Ephemeral */}
                              <div>
                                <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                                  Ephemeral
                                </h4>
                                <p className="text-sm text-gray-900">
                                  {flavor.ephemeral_gb ? `${flavor.ephemeral_gb} GB` : 'None'}
                                </p>
                              </div>
                              {/* RxTx Factor */}
                              <div>
                                <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                                  RxTx Factor
                                </h4>
                                <p className="text-sm text-gray-900">{flavor.rxtx_factor || '-'}</p>
                              </div>
                              {/* Status */}
                              <div>
                                <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                                  Status
                                </h4>
                                <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                                  {flavor.status}
                                </span>
                              </div>
                              {/* Created */}
                              <div>
                                <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                                  Created
                                </h4>
                                <p className="text-xs text-gray-600">
                                  {flavor.created_at
                                    ? new Date(flavor.created_at).toLocaleDateString()
                                    : '-'}
                                </p>
                              </div>
                            </div>
                          </td>
                        </tr>
                        <tr className="bg-gray-50">
                          <td colSpan={7} className="px-6 py-4">
                            <MetadataViewer
                              metadata={flavor.metadata}
                              name={`Metadata - ${flavor.name}`}
                            />
                          </td>
                        </tr>
                      </>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default FlavorList;
