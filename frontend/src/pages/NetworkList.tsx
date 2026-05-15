import React, { useEffect, useState } from 'react';
import { networkService } from '../services/networkService';
import { useCloudStore } from '../stores/cloudStore';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { MetadataViewer } from '../components/common/MetadataViewer';
import type { components } from '../types/api';

type NetworkResponse = components['schemas']['NetworkResponse'];

export const NetworkList: React.FC = () => {
  const { activeCloud, activeClouds } = useCloudStore();
  const [networks, setNetworks] = useState<NetworkResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedNetworkId, setExpandedNetworkId] = useState<string | null>(null);

  const loadNetworks = async (cloud: string) => {
    try {
      setLoading(true);
      setNetworks([]);
      const response = await networkService.listNetworks(100, 0, cloud);
      setNetworks(response);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load networks';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeClouds.length > 0 && activeCloud) {
      loadNetworks(activeCloud);
    }
  }, [activeCloud, activeClouds]);

  const toggleExpand = (networkId: string) => {
    setExpandedNetworkId(expandedNetworkId === networkId ? null : networkId);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Networks</h1>
        <p className="text-gray-600 mt-1">
          {networks.length} network{networks.length !== 1 ? 's' : ''} available
        </p>
      </div>

      {error && <ErrorAlert message={error} onClose={() => setError(null)} />}

      {loading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner message="Loading networks..." />
        </div>
      ) : networks.length === 0 ? (
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
              d="M9.75 17L9 20m0 0l-.75 3M9 20a6 6 0 1112 0m-8-3l.75-3m0 0l.75 3M21 20a6 6 0 11-12 0m8-3l-.75-3m0 0l-.75 3"
            />
          </svg>
          <p className="text-gray-600 text-lg">No networks found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {networks.map((network) => (
            <div key={network.id} className="bg-white rounded-lg shadow overflow-hidden">
              <div
                className="px-6 py-4 border-b border-gray-200 hover:bg-gray-50 cursor-pointer transition"
                onClick={() => toggleExpand(network.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center transition transform ${
                          expandedNetworkId === network.id ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d={expandedNetworkId === network.id ? 'M19 13l-7 7-7-7m14-8l-7 7-7-7' : 'M9 5l7 7-7 7'}
                          />
                        </svg>
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900">{network.name}</h3>
                        <p className="text-sm text-gray-600">{network.id}</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 ml-4">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        network.status === 'ACTIVE'
                          ? 'bg-green-100 text-green-800'
                          : network.status === 'DOWN'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {network.status}
                    </span>
                    {network.is_external && (
                      <span className="px-2 py-1 rounded text-xs font-semibold bg-purple-100 text-purple-800">
                        External
                      </span>
                    )}
                    {network.is_shared && (
                      <span className="px-2 py-1 rounded text-xs font-semibold bg-blue-100 text-blue-800">
                        Shared
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {expandedNetworkId === network.id && (
                <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <dt className="text-xs font-semibold text-gray-600 uppercase tracking-wider">Description</dt>
                      <dd className="mt-1 text-sm text-gray-900">{network.description || '-'}</dd>
                    </div>
                    <div>
                      <dt className="text-xs font-semibold text-gray-600 uppercase tracking-wider">MTU</dt>
                      <dd className="mt-1 text-sm text-gray-900">{network.mtu || '-'} bytes</dd>
                    </div>
                    <div>
                      <dt className="text-xs font-semibold text-gray-600 uppercase tracking-wider">External</dt>
                      <dd className="mt-1 text-sm text-gray-900">{network.is_external ? 'Yes' : 'No'}</dd>
                    </div>
                    <div>
                      <dt className="text-xs font-semibold text-gray-600 uppercase tracking-wider">Shared</dt>
                      <dd className="mt-1 text-sm text-gray-900">{network.is_shared ? 'Yes' : 'No'}</dd>
                    </div>
                    <div className="col-span-2">
                      <dt className="text-xs font-semibold text-gray-600 uppercase tracking-wider">Subnets</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {network.subnets && network.subnets.length > 0 ? (
                          <div className="space-y-1">
                            {network.subnets.map((subnet) => (
                              <div key={subnet} className="font-mono text-xs bg-gray-200 px-2 py-1 rounded">
                                {subnet}
                              </div>
                            ))}
                          </div>
                        ) : (
                          '-'
                        )}
                      </dd>
                    </div>
                  </div>

                  {network.metadata && Object.keys(network.metadata).length > 0 && (
                    <div className="pt-4 border-t border-gray-300">
                      <MetadataViewer metadata={network.metadata} />
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NetworkList;
