import React, { useEffect } from 'react';
import { useCloudStore } from '../stores/cloudStore';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const Settings: React.FC = () => {
  const { activeClouds, activeCloud, healthStatus, loading, fetchCloudsStatus } =
    useCloudStore();

  useEffect(() => {
    fetchCloudsStatus();
  }, [fetchCloudsStatus]);

  const isHealthy = healthStatus?.status === 'ok' || healthStatus?.status === 'healthy';

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">System configuration and status</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner message="Loading settings..." />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Cloud Configuration */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Cloud Configuration</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Active Cloud
                </label>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-blue-900 font-semibold">{activeCloud || 'Not set'}</p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Available Clouds
                </label>
                <div className="space-y-2">
                  {activeClouds.length > 0 ? (
                    activeClouds.map((cloud) => (
                      <div
                        key={cloud.name}
                        className="flex items-center gap-2 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg"
                      >
                        <svg
                          className="w-4 h-4 text-green-600"
                          fill="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                        </svg>
                        <div className="flex-1">
                          <span className="text-gray-700 font-medium">{cloud.name}</span>
                          <div className="text-xs text-gray-500 capitalize">
                            {cloud.type}
                            {cloud.authenticated && ' • Authenticated'}
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-sm">No clouds configured</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Health Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">API Health</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <div
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
                    isHealthy
                      ? 'bg-green-50 border border-green-200'
                      : 'bg-red-50 border border-red-200'
                  }`}
                >
                  <div
                    className={`w-3 h-3 rounded-full ${
                      isHealthy ? 'bg-green-600' : 'bg-red-600'
                    }`}
                  />
                  <span
                    className={`font-semibold ${
                      isHealthy ? 'text-green-900' : 'text-red-900'
                    }`}
                  >
                    {isHealthy ? 'Healthy' : 'Unhealthy'}
                  </span>
                </div>
              </div>

              {healthStatus && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Last Check
                    </label>
                    <p className="text-gray-600 text-sm">
                      {new Date(healthStatus.timestamp).toLocaleString()}
                    </p>
                  </div>

                  {healthStatus.version && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        API Version
                      </label>
                      <p className="text-gray-600 text-sm">{healthStatus.version}</p>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* API Configuration */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">API Configuration</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Endpoint
                </label>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                  <p className="text-gray-600 text-sm font-mono break-all">
                    {import.meta.env.VITE_API_URL || 'http://localhost:8000'}
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Request Timeout
                </label>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                  <p className="text-gray-600 text-sm font-mono">
                    {(parseInt(import.meta.env.VITE_API_TIMEOUT || '30000') / 1000).toFixed(0)}s
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Application Info</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Application
                </label>
                <p className="text-gray-600 text-sm">OpenStack VM Orchestrator</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Frontend Framework
                </label>
                <p className="text-gray-600 text-sm">React 18+ with TypeScript</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  State Management
                </label>
                <p className="text-gray-600 text-sm">Zustand</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;
