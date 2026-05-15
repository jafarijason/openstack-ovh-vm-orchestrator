import React, { useEffect } from 'react';
import { useCloudStore } from '../../stores/cloudStore';

export const Header: React.FC = () => {
  const { activeCloud, healthStatus, checkHealth } = useCloudStore();

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check health every 30 seconds
    return () => clearInterval(interval);
  }, [checkHealth]);

  const isHealthy = healthStatus?.status === 'ok' || healthStatus?.status === 'healthy';

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
            {activeCloud && (
              <div className="text-sm">
                <span className="text-gray-600">Active Cloud: </span>
                <span className="font-semibold text-gray-900">{activeCloud}</span>
              </div>
            )}

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
