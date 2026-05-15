import React, { useEffect, useState } from 'react';
import { useCloudStore } from '../../stores/cloudStore';

export const Header: React.FC = () => {
  const { activeClouds, activeCloud, healthStatus, checkHealth, fetchCloudsStatus, switchCloud } = useCloudStore();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    fetchCloudsStatus();
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check health every 30 seconds
    return () => clearInterval(interval);
  }, [fetchCloudsStatus, checkHealth]);

  const isHealthy = healthStatus?.status === 'ok' || healthStatus?.status === 'healthy';

  const handleCloudSelect = (cloudName: string) => {
    switchCloud(cloudName);
    setIsDropdownOpen(false);
  };

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <svg
                className="w-8 h-8 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 3v2m6-2v2m-9 4v10a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2zm0 0a2 2 0 012-2h10a2 2 0 012 2m0 0V5m0 10H3"
                />
              </svg>
              <h1 className="text-2xl font-bold text-gray-800">
                OpenStack VM Orchestrator
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-6">
            {/* Cloud Picker Dropdown */}
            {activeClouds.length > 0 && (
              <div className="relative">
                <button
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors font-medium text-sm border border-blue-200"
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                    />
                  </svg>
                  <span>{activeCloud || 'Select Cloud'}</span>
                  <svg
                    className={`w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 14l-7 7m0 0l-7-7m7 7V3"
                    />
                  </svg>
                </button>

                {/* Dropdown Menu */}
                {isDropdownOpen && (
                  <div className="absolute top-full right-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
                    <div className="p-2">
                      {activeClouds.map((cloud) => (
                        <button
                          key={cloud.name}
                          onClick={() => handleCloudSelect(cloud.name)}
                          className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                            activeCloud === cloud.name
                              ? 'bg-blue-100 text-blue-900 font-semibold'
                              : 'hover:bg-gray-100 text-gray-700'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-medium">{cloud.name}</div>
                              <div className="text-xs text-gray-500 capitalize">
                                {cloud.type}
                                {cloud.authenticated && ' • Authenticated'}
                              </div>
                            </div>
                            {activeCloud === cloud.name && (
                              <svg
                                className="w-4 h-4 text-blue-600"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                              >
                                <path
                                  fillRule="evenodd"
                                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                  clipRule="evenodd"
                                />
                              </svg>
                            )}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Health Status */}
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  isHealthy ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-gray-600">
                {isHealthy ? 'Operational' : 'Degraded'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
